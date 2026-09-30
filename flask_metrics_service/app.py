"""Servicio aislado de métricas de salud para la migración Strangler Pattern."""

from datetime import UTC, datetime
from hashlib import sha256

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


def create_app() -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "health-metrics"})

    @app.get("/api/v2/health-metrics/<user_id>/")
    def get_health_metrics(user_id: str):
        normalized_user_id = user_id.strip()
        if not normalized_user_id:
            return jsonify({"error": "user_id is required"}), 400

        # La semilla determinista simplifica la trazabilidad mientras se conecta
        # el proveedor real de wearables, sin depender de la base del monolito.
        digest = sha256(normalized_user_id.encode("utf-8")).digest()
        metrics = {
            "user_id": normalized_user_id,
            "pulse_bpm": 52 + digest[0] % 47,
            "sleep_hours": round(5.2 + (digest[1] / 255) * 3.3, 1),
            "training_load": 30 + digest[2] % 66,
            "generated_at": datetime.now(UTC).isoformat(),
            "source": "flask-health-metrics-service",
        }
        return jsonify(metrics), 200

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
