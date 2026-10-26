from typing import Protocol


class WeatherPort(Protocol):
    def current_conditions(self, latitude: float, longitude: float) -> dict: ...


class AllyPort(Protocol):
    def fetch_summary(self) -> dict: ...
