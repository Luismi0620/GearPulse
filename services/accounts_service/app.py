import os
import uuid
from datetime import UTC, datetime

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False, default="athlete")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
        }


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///accounts.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JSON_SORT_KEYS=False,
    )
    if config:
        app.config.update(config)
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health_check():
        db.session.execute(db.select(User.id).limit(1))
        return jsonify({"status": "ok", "service": "accounts"})

    @app.post("/api/v2/users/register/")
    def register_user():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error("invalid_json", "A JSON object is required.", 400)

        email = str(payload.get("email", "")).strip().lower()
        role = str(payload.get("role", "athlete")).strip().lower()
        if not email or "@" not in email:
            return _error("invalid_email", "A valid email is required.", 400)
        if role not in {"athlete", "admin"}:
            return _error("invalid_role", "Role must be athlete or admin.", 400)

        user = User(email=email, role=role)
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _error("email_conflict", "The email is already registered.", 409)
        return jsonify(user.to_dict()), 201

    @app.get("/api/v2/users/<user_id>/")
    def get_user(user_id: str):
        user = db.session.get(User, user_id)
        if user is None:
            return _error("user_not_found", "The user does not exist.", 404)
        return jsonify(user.to_dict())

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return _error(error.name.lower().replace(" ", "_"), error.description, error.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected accounts service error", exc_info=error)
        return _error("internal_error", "An internal error occurred.", 500)

    return app


app = create_app()
