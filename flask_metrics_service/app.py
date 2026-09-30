"""Servicio aislado de métricas de salud para la migración Strangler Pattern."""

from datetime import UTC, datetime
from hashlib import sha256

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


def create_app() -> Flask:
    app = Flask(__name__)

    def build_metrics(user_id: str) -> dict:
        normalized_user_id = user_id.strip()
        if not normalized_user_id:
            raise ValueError("user_id is required")

        # La semilla determinista simplifica la trazabilidad mientras se conecta
        # el proveedor real de wearables, sin depender de la base del monolito.
        digest = sha256(normalized_user_id.encode("utf-8")).digest()
        return {
            "user_id": normalized_user_id,
            "pulse_bpm": 52 + digest[0] % 47,
            "sleep_hours": round(5.2 + (digest[1] / 255) * 3.3, 1),
            "training_load": 30 + digest[2] % 66,
            "generated_at": datetime.now(UTC).isoformat(),
            "source": "flask-health-metrics-service",
        }

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "health-metrics"})

    @app.get("/api/v2/health-metrics/<user_id>/")
    def get_health_metrics(user_id: str):
        try:
            return jsonify(build_metrics(user_id)), 200
        except ValueError as error:
            return jsonify({"error": str(error), "status": 400}), 400

    @app.post("/api/v2/health-metrics/")
    def create_health_metrics():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "a JSON object is required", "status": 400}), 400

        user_id = payload.get("user_id")
        if not isinstance(user_id, str):
            return jsonify({"error": "user_id is required", "status": 400}), 400

        try:
            return jsonify(build_metrics(user_id)), 200
        except ValueError as error:
            return jsonify({"error": str(error), "status": 400}), 400

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return jsonify({"error": error.name, "status": error.code}), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected health metrics service error", exc_info=error)
        return jsonify({"error": "internal server error", "status": 500}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
