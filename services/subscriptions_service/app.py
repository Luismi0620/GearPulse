import os
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from requests.adapters import HTTPAdapter
from sqlalchemy.exc import IntegrityError
from urllib3.util.retry import Retry
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()
PLAN_DATA = {
    "monthly": (Decimal("19.90"), 30),
    "quarterly": (Decimal("49.90"), 90),
    "yearly": (Decimal("179.90"), 365),
}


class Plan(db.Model):
    __tablename__ = "plans"
    name = db.Column(db.String(20), primary_key=True)
    price = db.Column(db.Numeric(8, 2), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)

    def to_dict(self) -> dict:
        return {"name": self.name, "price": f"{self.price:.2f}", "duration_days": self.duration_days}


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    plan = db.Column(db.String(20), nullable=False)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    def is_active(self) -> bool:
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return self.active and expires_at > datetime.now(UTC)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "plan": self.plan,
            "status": "active" if self.is_active() else "inactive",
            "started_at": self.started_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }


def _session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=2, backoff_factor=0.2, status_forcelist=(502, 503, 504), allowed_methods=("GET",))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///subscriptions.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        ACCOUNT_SERVICE_URL=os.getenv("ACCOUNT_SERVICE_URL", "http://accounts_service:5000"),
        ASYNC_SERVICE_URL=os.getenv("ASYNC_SERVICE_URL", "http://async_api:5000"),
        HTTP_TIMEOUT=float(os.getenv("HTTP_TIMEOUT", "3")),
    )
    if config:
        app.config.update(config)
    db.init_app(app)

    with app.app_context():
        db.create_all()
        for name, (price, duration) in PLAN_DATA.items():
            if db.session.get(Plan, name) is None:
                db.session.add(Plan(name=name, price=price, duration_days=duration))
        db.session.commit()

    def user_exists(user_id: str) -> bool:
        validator = app.config.get("ACCOUNT_VALIDATOR")
        if validator:
            return bool(validator(user_id))
        response = _session().get(
            f"{app.config['ACCOUNT_SERVICE_URL']}/api/v2/users/{user_id}/",
            timeout=app.config["HTTP_TIMEOUT"],
        )
        return response.status_code == 200

    def enqueue_notification(subscription: Subscription) -> None:
        if app.config.get("TESTING"):
            return
        try:
            requests.post(
                f"{app.config['ASYNC_SERVICE_URL']}/api/v2/notifications/subscription-activated/",
                json=subscription.to_dict(),
                timeout=app.config["HTTP_TIMEOUT"],
            ).raise_for_status()
        except requests.RequestException:
            app.logger.warning("Notification service unavailable; activation remains committed")

    @app.get("/health")
    def health_check():
        db.session.execute(db.select(Plan.name).limit(1))
        return jsonify({"status": "ok", "service": "subscriptions"})

    @app.get("/api/v2/plans/")
    def list_plans():
        plans = db.session.scalars(db.select(Plan).order_by(Plan.duration_days)).all()
        return jsonify([plan.to_dict() for plan in plans])

    @app.post("/api/v2/subscriptions/activate/")
    def activate_subscription():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error("invalid_json", "A JSON object is required.", 400)
        user_id = str(payload.get("user_id", "")).strip()
        plan_name = str(payload.get("plan", "")).strip().lower()
        plan = db.session.get(Plan, plan_name)
        if not user_id:
            return _error("missing_user_id", "user_id is required.", 400)
        if plan is None:
            return _error("invalid_plan", "The selected plan does not exist.", 400)
        try:
            exists = user_exists(user_id)
        except requests.RequestException:
            return _error("accounts_unavailable", "The accounts service is temporarily unavailable.", 503)
        if not exists:
            return _error("user_not_found", "The user does not exist.", 404)

        current = db.session.scalar(
            db.select(Subscription).where(Subscription.user_id == user_id, Subscription.active.is_(True))
        )
        if current and current.is_active():
            return _error("subscription_conflict", "The user already has an active subscription.", 409)

        now = datetime.now(UTC)
        subscription = Subscription(
            user_id=user_id,
            plan=plan.name,
            started_at=now,
            expires_at=now + timedelta(days=plan.duration_days),
        )
        db.session.add(subscription)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _error("subscription_conflict", "The subscription could not be created.", 409)
        enqueue_notification(subscription)
        return jsonify(subscription.to_dict()), 201

    @app.get("/internal/subscriptions/<user_id>/active/")
    def active_subscription(user_id: str):
        subscription = db.session.scalar(
            db.select(Subscription).where(Subscription.user_id == user_id, Subscription.active.is_(True))
        )
        return jsonify({"user_id": user_id, "active": bool(subscription and subscription.is_active())})

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return _error(error.name.lower().replace(" ", "_"), error.description, error.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected subscriptions service error", exc_info=error)
        return _error("internal_error", "An internal error occurred.", 500)

    return app


app = create_app()
