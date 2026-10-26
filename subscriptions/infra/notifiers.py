import logging

from subscriptions.domain.entities import Subscription
from subscriptions.domain.ports import Notifier

logger = logging.getLogger(__name__)


class ConsoleNotifier(Notifier):
    def send_subscription_activated(self, subscription: Subscription) -> None:
        logger.info(
            "Subscription activated for user=%s plan=%s",
            subscription.user_id,
            subscription.plan,
        )


class MockNotifier(Notifier):
    def send_subscription_activated(self, subscription: Subscription) -> None:
        logger.debug(
            "MOCK notification for user=%s plan=%s",
            subscription.user_id,
            subscription.plan,
        )
