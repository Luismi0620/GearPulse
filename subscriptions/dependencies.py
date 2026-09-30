from subscriptions.application.services import SubscriptionService
from subscriptions.infra.metrics_provider import SimulatedMetricsProvider
from subscriptions.infra.notifier_factory import NotifierFactory
from subscriptions.infra.repositories import OrmSubscriptionRepository

# Composition root for dependency injection.
_repository = OrmSubscriptionRepository()


def get_subscription_service() -> SubscriptionService:
    return SubscriptionService(
        repository=_repository,
        notifier=NotifierFactory.create(),
        metrics_provider=SimulatedMetricsProvider(),
    )
