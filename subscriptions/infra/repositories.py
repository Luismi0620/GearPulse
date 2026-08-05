from subscriptions.domain.entities import Subscription
from subscriptions.domain.ports import SubscriptionRepository


class InMemorySubscriptionRepository(SubscriptionRepository):
    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}

    def save(self, subscription: Subscription) -> None:
        self._subscriptions[subscription.user_id] = subscription

    def find_active_by_user(self, user_id: str) -> Subscription | None:
        subscription = self._subscriptions.get(user_id)
        if subscription and subscription.is_active():
            return subscription
        return None
