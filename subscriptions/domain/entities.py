from dataclasses import dataclass, field
from datetime import datetime

from django.utils import timezone


@dataclass(frozen=True)
class Subscription:
    user_id: str
    plan: str
    started_at: datetime
    expires_at: datetime
    active: bool = field(default=True)

    def is_active(self, now: datetime | None = None) -> bool:
        check_time = now or timezone.now()
        return self.active and self.expires_at > check_time


@dataclass(frozen=True)
class HealthMetrics:
    pulse_bpm: int
    sleep_hours: float
    training_load: int
    generated_at: datetime
