from django.core.exceptions import ValidationError

from subscriptions.domain.entities import Subscription
from subscriptions.domain.ports import SubscriptionRepository

from .models import SubscriptionModel


def _to_entity(row: SubscriptionModel) -> Subscription:
    return Subscription(
        user_id=str(row.user_id),
        plan=row.plan,
        started_at=row.started_at,
        expires_at=row.expires_at,
        active=row.active,
    )


class InMemorySubscriptionRepository(SubscriptionRepository):
    """Kept for fast, DB-less unit tests of the service layer."""

    def __init__(self) -> None:
        self._subscriptions: dict[str, Subscription] = {}

    def save(self, subscription: Subscription) -> None:
        self._subscriptions[subscription.user_id] = subscription

    def find_active_by_user(self, user_id: str) -> Subscription | None:
        subscription = self._subscriptions.get(user_id)
        if subscription and subscription.is_active():
            return subscription
        return None


class OrmSubscriptionRepository(SubscriptionRepository):
    """Production repository, backed by the real database."""

    def save(self, subscription: Subscription) -> None:
        SubscriptionModel.objects.update_or_create(
            user_id=subscription.user_id,
            defaults={
                "plan": subscription.plan,
                "started_at": subscription.started_at,
                "expires_at": subscription.expires_at,
                "active": subscription.active,
            },
        )

    def find_active_by_user(self, user_id: str) -> Subscription | None:
        try:
            row = SubscriptionModel.objects.filter(user_id=user_id).first()
        except ValidationError:
            # user_id is not a well-formed identifier -> treat as "no subscription".
            return None
        if row is None:
            return None
        entity = _to_entity(row)
        return entity if entity.is_active() else None
