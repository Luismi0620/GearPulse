"""Independent health metrics service extracted with the Strangler Pattern."""

import os
from datetime import UTC, datetime
from hashlib import sha256

import requests
from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        SUBSCRIPTIONS_SERVICE_URL=os.getenv(
            "SUBSCRIPTIONS_SERVICE_URL", "http://subscriptions_service:5000"
        ),
        HTTP_TIMEOUT=float(os.getenv("HTTP_TIMEOUT", "3")),
        VERIFY_SUBSCRIPTION=os.getenv("VERIFY_SUBSCRIPTION", "true").lower() == "true",
    )
    if config:
        app.config.update(config)

    def has_active_subscription(user_id: str) -> bool:
        verifier = app.config.get("SUBSCRIPTION_VALIDATOR")
        if verifier:
            return bool(verifier(user_id))
        if not app.config["VERIFY_SUBSCRIPTION"]:
            return True
        response = requests.get(
            f"{app.config['SUBSCRIPTIONS_SERVICE_URL']}/internal/subscriptions/{user_id}/active/",
            timeout=app.config["HTTP_TIMEOUT"],
        )
        response.raise_for_status()
        return bool(response.json().get("active"))

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
            if not has_active_subscription(user_id):
                return jsonify({"error": "active subscription required", "status": 403}), 403
            return jsonify(build_metrics(user_id)), 200
        except requests.RequestException:
            return jsonify({"error": "subscriptions service unavailable", "status": 503}), 503
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
            if not has_active_subscription(user_id):
                return jsonify({"error": "active subscription required", "status": 403}), 403
            return jsonify(build_metrics(user_id)), 200
        except requests.RequestException:
            return jsonify({"error": "subscriptions service unavailable", "status": 503}), 503
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
