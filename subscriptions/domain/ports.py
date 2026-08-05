from abc import ABC, abstractmethod

from .entities import HealthMetrics, Subscription


class SubscriptionRepository(ABC):
    @abstractmethod
    def save(self, subscription: Subscription) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_active_by_user(self, user_id: str) -> Subscription | None:
        raise NotImplementedError


class Notifier(ABC):
    @abstractmethod
    def send_subscription_activated(self, subscription: Subscription) -> None:
        raise NotImplementedError


class MetricsProvider(ABC):
    @abstractmethod
    def get_metrics(self, user_id: str) -> HealthMetrics:
        raise NotImplementedError
