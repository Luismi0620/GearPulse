from django.test import Client, TestCase

from accounts.models import User
from common.exceptions import ConflictError, NotFoundError
from subscriptions.application.services import SubscriptionService
from subscriptions.infra.metrics_provider import SimulatedMetricsProvider
from subscriptions.infra.notifiers import MockNotifier
from subscriptions.infra.repositories import InMemorySubscriptionRepository, OrmSubscriptionRepository


class SubscriptionServiceUnitTests(TestCase):
    """Fast unit tests against the in-memory repository (no DB round trips)."""

    def setUp(self):
        self.user = User.objects.create(email="unit@test.com", role=User.Role.ATHLETE)
        self.repository = InMemorySubscriptionRepository()
        self.service = SubscriptionService(
            repository=self.repository,
            notifier=MockNotifier(),
            metrics_provider=SimulatedMetricsProvider(),
        )

    def test_activate_subscription_creates_active_record(self):
        subscription = self.service.activate_subscription(str(self.user.id), "monthly")
        self.assertEqual(subscription.user_id, str(self.user.id))
        self.assertTrue(subscription.is_active())

    def test_get_metrics_requires_active_subscription(self):
        with self.assertRaises(ValueError):
            self.service.get_user_metrics("u-without-plan")

    def test_activate_subscription_rejects_unknown_user(self):
        with self.assertRaises(NotFoundError):
            self.service.activate_subscription("00000000-0000-0000-0000-000000000000", "monthly")

    def test_activate_subscription_rejects_duplicate(self):
        self.service.activate_subscription(str(self.user.id), "monthly")
        with self.assertRaises(ConflictError):
            self.service.activate_subscription(str(self.user.id), "monthly")


class SubscriptionOrmRepositoryTests(TestCase):
    """Confirms the production repository round-trips through the real database."""

    def setUp(self):
        self.user = User.objects.create(email="orm@test.com")
        self.service = SubscriptionService(
            repository=OrmSubscriptionRepository(),
            notifier=MockNotifier(),
            metrics_provider=SimulatedMetricsProvider(),
        )

    def test_activate_and_find_persists_to_db(self):
        self.service.activate_subscription(str(self.user.id), "yearly")
        active = self.service.get_user_metrics(str(self.user.id))
        self.assertIsNotNone(active)


class StranglerBoundaryTests(TestCase):
    def test_legacy_subscription_route_is_no_longer_exposed_by_django(self):
        response = Client().post("/subscription/activate/", data={}, content_type="application/json")
        self.assertEqual(response.status_code, 404)
