from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from .celery_app import celery
from .tasks import generate_workout_report, notify_subscription


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    if config:
        app.config.update(config)
        celery.conf.update(config.get("CELERY", {}))

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "async-jobs"})

    @app.post("/api/v2/notifications/subscription-activated/")
    def subscription_notification():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not payload.get("user_id") or not payload.get("plan"):
            return _error("invalid_event", "user_id and plan are required.", 400)
        task = notify_subscription.delay(payload)
        return jsonify({"task_id": task.id, "status": "queued"}), 202

    @app.post("/api/v2/reports/workout/")
    def workout_report():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict) or not payload.get("id"):
            return _error("invalid_event", "A workout id is required.", 400)
        task = generate_workout_report.delay(payload)
        return jsonify({"task_id": task.id, "status": "queued"}), 202

    @app.get("/api/v2/tasks/<task_id>/")
    def task_status(task_id: str):
        task = celery.AsyncResult(task_id)
        data = {"task_id": task_id, "status": task.state.lower()}
        if task.successful():
            data["result"] = task.result
        elif task.failed():
            data["error"] = "Task execution failed."
        return jsonify(data)

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return _error(error.name.lower().replace(" ", "_"), error.description, error.code or 500)

    return app


app = create_app()
