import random

from django.utils import timezone

from subscriptions.domain.entities import HealthMetrics
from subscriptions.domain.ports import MetricsProvider


class SimulatedMetricsProvider(MetricsProvider):
    def get_metrics(self, user_id: str) -> HealthMetrics:
        now = timezone.now()
        seed = sum(ord(char) for char in user_id) + now.minute
        random.seed(seed)
        return HealthMetrics(
            pulse_bpm=random.randint(52, 98),
            sleep_hours=round(random.uniform(5.2, 8.5), 1),
            training_load=random.randint(30, 95),
            generated_at=now,
        )
