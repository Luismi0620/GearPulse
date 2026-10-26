import os
import uuid
from datetime import UTC, datetime

import requests
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from requests.adapters import HTTPAdapter
from sqlalchemy.exc import IntegrityError
from urllib3.util.retry import Retry
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()


class Device(db.Model):
    __tablename__ = "devices"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    brand = db.Column(db.String(80), nullable=False)
    model = db.Column(db.String(80), nullable=False)
    serial_number = db.Column(db.String(64), unique=True, nullable=False)
    paired_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    active = db.Column(db.Boolean, nullable=False, default=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "brand": self.brand,
            "model": self.model,
            "serial_number": self.serial_number,
            "paired_at": self.paired_at.isoformat(),
            "active": self.active,
        }


class Workout(db.Model):
    __tablename__ = "workouts"
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = db.Column(db.String(36), db.ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time = db.Column(db.DateTime(timezone=True), nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    avg_heart_rate = db.Column(db.Integer, nullable=False)

    def to_dict(self) -> dict:
        start = self.start_time.replace(tzinfo=self.start_time.tzinfo or UTC)
        end = self.end_time.replace(tzinfo=self.end_time.tzinfo or UTC)
        return {
            "id": self.id,
            "device_id": self.device_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "calories": self.calories,
            "avg_heart_rate": self.avg_heart_rate,
            "duration_minutes": round((end - start).total_seconds() / 60, 1),
        }


def _session() -> requests.Session:
    session = requests.Session()
    retry = Retry(total=2, backoff_factor=0.2, status_forcelist=(502, 503, 504), allowed_methods=("GET",))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def _parse_datetime(value) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    except ValueError:
        return None


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///activity.db"),
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

    def user_exists(user_id: str) -> bool:
        validator = app.config.get("ACCOUNT_VALIDATOR")
        if validator:
            return bool(validator(user_id))
        response = _session().get(
            f"{app.config['ACCOUNT_SERVICE_URL']}/api/v2/users/{user_id}/",
            timeout=app.config["HTTP_TIMEOUT"],
        )
        return response.status_code == 200

    def enqueue_report(workout: Workout) -> None:
        if app.config.get("TESTING"):
            return
        try:
            requests.post(
                f"{app.config['ASYNC_SERVICE_URL']}/api/v2/reports/workout/",
                json=workout.to_dict(),
                timeout=app.config["HTTP_TIMEOUT"],
            ).raise_for_status()
        except requests.RequestException:
            app.logger.warning("Async report service unavailable; workout remains committed")

    @app.get("/health")
    def health_check():
        db.session.execute(db.select(Device.id).limit(1))
        return jsonify({"status": "ok", "service": "activity"})

    @app.post("/api/v2/devices/pair/")
    def pair_device():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error("invalid_json", "A JSON object is required.", 400)
        values = {key: str(payload.get(key, "")).strip() for key in ("user_id", "brand", "model", "serial_number")}
        values["serial_number"] = values["serial_number"].upper()
        missing = [key for key, value in values.items() if not value]
        if missing:
            return _error("missing_fields", f"Required fields: {', '.join(missing)}.", 400)
        if len(values["serial_number"]) < 6:
            return _error("invalid_serial", "serial_number must contain at least 6 characters.", 400)
        try:
            exists = user_exists(values["user_id"])
        except requests.RequestException:
            return _error("accounts_unavailable", "The accounts service is temporarily unavailable.", 503)
        if not exists:
            return _error("user_not_found", "The user does not exist.", 404)

        device = Device(**values)
        db.session.add(device)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return _error("serial_conflict", "The serial number is already paired.", 409)
        return jsonify(device.to_dict()), 201

    @app.route("/api/v2/devices/<device_id>/workouts/", methods=["GET", "POST"])
    def device_workouts(device_id: str):
        device = db.session.get(Device, device_id)
        if device is None:
            return _error("device_not_found", "The device does not exist.", 404)
        if request.method == "GET":
            workouts = db.session.scalars(
                db.select(Workout).where(Workout.device_id == device_id).order_by(Workout.start_time.desc())
            ).all()
            return jsonify([workout.to_dict() for workout in workouts])

        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error("invalid_json", "A JSON object is required.", 400)
        start = _parse_datetime(payload.get("start_time"))
        end = _parse_datetime(payload.get("end_time"))
        try:
            calories = int(payload.get("calories"))
            heart_rate = int(payload.get("avg_heart_rate"))
        except (TypeError, ValueError):
            return _error("invalid_metrics", "Calories and heart rate must be integers.", 400)
        if start is None or end is None or end <= start:
            return _error("invalid_time_range", "end_time must be after start_time.", 400)
        if calories < 0 or heart_rate <= 0:
            return _error("invalid_metrics", "Calories and heart rate are outside the valid range.", 400)

        workout = Workout(
            device_id=device_id,
            start_time=start,
            end_time=end,
            calories=calories,
            avg_heart_rate=heart_rate,
        )
        db.session.add(workout)
        db.session.commit()
        enqueue_report(workout)
        return jsonify(workout.to_dict()), 201

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return _error(error.name.lower().replace(" ", "_"), error.description, error.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected activity service error", exc_info=error)
        return _error("internal_error", "An internal error occurred.", 500)

    return app


app = create_app()
