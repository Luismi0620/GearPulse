import os

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from .adapters import AllyServiceAdapter, IntegrationUnavailable, OpenMeteoAdapter


def _error(code: str, message: str, status: int):
    return jsonify({"error": {"code": code, "message": message}}), status


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(
        OPEN_METEO_URL=os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com"),
        ALLY_SERVICE_URL=os.getenv("ALLY_SERVICE_URL", ""),
        HTTP_TIMEOUT=float(os.getenv("HTTP_TIMEOUT", "4")),
    )
    if config:
        app.config.update(config)

    weather = app.config.get("WEATHER_ADAPTER") or OpenMeteoAdapter(
        app.config["OPEN_METEO_URL"], app.config["HTTP_TIMEOUT"]
    )
    ally = app.config.get("ALLY_ADAPTER") or AllyServiceAdapter(
        app.config["ALLY_SERVICE_URL"], app.config["HTTP_TIMEOUT"]
    )

    @app.get("/health")
    def health_check():
        return jsonify({"status": "ok", "service": "integrations"})

    @app.get("/api/v2/integrations/weather/")
    def weather_conditions():
        try:
            latitude = float(request.args.get("latitude", "6.2442"))
            longitude = float(request.args.get("longitude", "-75.5812"))
        except ValueError:
            return _error("invalid_coordinates", "Latitude and longitude must be numeric.", 400)
        if not -90 <= latitude <= 90 or not -180 <= longitude <= 180:
            return _error("invalid_coordinates", "Coordinates are outside the valid range.", 400)
        try:
            return jsonify(weather.current_conditions(latitude, longitude))
        except IntegrationUnavailable as exc:
            return _error("weather_unavailable", str(exc), 503)

    @app.get("/api/v2/integrations/ally/")
    def ally_summary():
        try:
            return jsonify(ally.fetch_summary())
        except IntegrationUnavailable as exc:
            return _error("ally_unavailable", str(exc), 503)

    @app.get("/api/v2/public/summary/")
    def public_summary():
        """JSON contract provided to the allied team and course evaluators."""
        return jsonify(
            {
                "service": "GearPulse",
                "version": "2.0",
                "status": "operational",
                "capabilities": [
                    "user-registration",
                    "subscription-management",
                    "device-pairing",
                    "workout-tracking",
                    "health-metrics",
                ],
                "contract": "/api/v2/public/summary/",
            }
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return _error(error.name.lower().replace(" ", "_"), error.description, error.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        app.logger.exception("Unexpected integration service error", exc_info=error)
        return _error("internal_error", "An internal error occurred.", 500)

    return app


app = create_app()
