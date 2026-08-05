from datetime import datetime, timedelta

from .entities import Subscription


PLAN_DURATION_DAYS = {
    "monthly": 30,
    "quarterly": 90,
    "yearly": 365,
}


class SubscriptionBuilder:
    def __init__(self) -> None:
        self._user_id: str | None = None
        self._plan: str | None = None
        self._started_at: datetime | None = None

    def for_user(self, user_id: str) -> "SubscriptionBuilder":
        self._user_id = user_id.strip() if user_id else ""
        return self

    def with_plan(self, plan: str) -> "SubscriptionBuilder":
        self._plan = plan.strip().lower() if plan else ""
        return self

    def starts_now(self) -> "SubscriptionBuilder":
        self._started_at = datetime.utcnow()
        return self

    def build(self) -> Subscription:
        if not self._user_id:
            raise ValueError("user_id is required")
        if self._plan not in PLAN_DURATION_DAYS:
            raise ValueError("invalid plan: use monthly, quarterly or yearly")

        started_at = self._started_at or datetime.utcnow()
        expires_at = started_at + timedelta(days=PLAN_DURATION_DAYS[self._plan])
        return Subscription(
            user_id=self._user_id,
            plan=self._plan,
            started_at=started_at,
            expires_at=expires_at,
        )
