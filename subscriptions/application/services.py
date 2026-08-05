from subscriptions.domain.builders import SubscriptionBuilder
from subscriptions.domain.entities import HealthMetrics, Subscription
from subscriptions.domain.ports import MetricsProvider, Notifier, SubscriptionRepository


class SubscriptionService:
    def __init__(
        self,
        repository: SubscriptionRepository,
        notifier: Notifier,
        metrics_provider: MetricsProvider,
    ) -> None:
        self._repository = repository
        self._notifier = notifier
        self._metrics_provider = metrics_provider

    def activate_subscription(self, user_id: str, plan: str) -> Subscription:
        subscription = (
            SubscriptionBuilder().for_user(user_id).with_plan(plan).starts_now().build()
        )
        self._repository.save(subscription)
        self._notifier.send_subscription_activated(subscription)
        return subscription

    def get_user_metrics(self, user_id: str) -> HealthMetrics:
        active_subscription = self._repository.find_active_by_user(user_id)
        if not active_subscription:
            raise ValueError("User has no active subscription")
        return self._metrics_provider.get_metrics(user_id)
