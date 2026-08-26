from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Device:
    id: str
    user_id: str
    brand: str
    model: str
    serial_number: str
    paired_at: datetime
    active: bool = True


@dataclass(frozen=True)
class WorkoutSession:
    id: str
    device_id: str
    start_time: datetime
    end_time: datetime
    calories: int
    avg_heart_rate: int

    def duration_minutes(self) -> float:
        return round((self.end_time - self.start_time).total_seconds() / 60, 1)
