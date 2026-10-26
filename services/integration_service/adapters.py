import time

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class IntegrationUnavailable(RuntimeError):
    pass


def resilient_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=2,
        read=2,
        backoff_factor=0.25,
        status_forcelist=(429, 502, 503, 504),
        allowed_methods=("GET",),
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    session.mount("http://", HTTPAdapter(max_retries=retry))
    return session


class OpenMeteoAdapter:
    """Adapter: translates Open-Meteo's contract into the GearPulse weather port."""

    def __init__(self, base_url: str, timeout: float = 4.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http = resilient_session()

    def current_conditions(self, latitude: float, longitude: float) -> dict:
        try:
            response = self._http.get(
                f"{self._base_url}/v1/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,apparent_temperature,precipitation,wind_speed_10m",
                    "timezone": "auto",
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
            current = response.json()["current"]
        except (requests.RequestException, KeyError, TypeError, ValueError) as exc:
            raise IntegrationUnavailable("Weather provider is temporarily unavailable.") from exc
        return {
            "provider": "open-meteo",
            "latitude": latitude,
            "longitude": longitude,
            "observed_at": current.get("time"),
            "temperature_c": current.get("temperature_2m"),
            "apparent_temperature_c": current.get("apparent_temperature"),
            "precipitation_mm": current.get("precipitation"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
        }


class AllyServiceAdapter:
    """Anti-corruption adapter for the allied team's independently owned API."""

    def __init__(self, url: str, timeout: float = 4.0, failure_threshold: int = 3) -> None:
        self._url = url
        self._timeout = timeout
        self._http = resilient_session()
        self._failures = 0
        self._opened_at = 0.0
        self._failure_threshold = failure_threshold

    def fetch_summary(self) -> dict:
        if not self._url:
            raise IntegrationUnavailable("ALLY_SERVICE_URL is not configured.")
        if self._failures >= self._failure_threshold and time.monotonic() - self._opened_at < 30:
            raise IntegrationUnavailable("Allied service circuit is temporarily open.")
        try:
            response = self._http.get(self._url, timeout=self._timeout)
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, (dict, list)):
                raise ValueError("Invalid ally payload")
        except (requests.RequestException, ValueError) as exc:
            self._failures += 1
            self._opened_at = time.monotonic()
            raise IntegrationUnavailable("Allied service is temporarily unavailable.") from exc
        self._failures = 0
        return {"source": "allied-team", "status": "available", "data": payload}
