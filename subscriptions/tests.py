import json

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


class SubscriptionViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(email="views@test.com")

    def test_activate_then_get_metrics(self):
        activate_response = self.client.post(
            "/subscription/activate/",
            data=json.dumps({"user_id": str(self.user.id), "plan": "monthly"}),
            content_type="application/json",
        )
        self.assertEqual(activate_response.status_code, 201)

        metrics_response = self.client.get(f"/subscription/{self.user.id}/metrics/")
        self.assertEqual(metrics_response.status_code, 200)

    def test_metrics_without_subscription_returns_403(self):
        metrics_response = self.client.get("/subscription/no-sub/metrics/")
        self.assertEqual(metrics_response.status_code, 403)

    def test_activate_unknown_user_returns_404(self):
        response = self.client.post(
            "/subscription/activate/",
            data=json.dumps({"user_id": "00000000-0000-0000-0000-000000000000", "plan": "monthly"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_activate_duplicate_subscription_returns_409(self):
        payload = json.dumps({"user_id": str(self.user.id), "plan": "monthly"})
        self.client.post("/subscription/activate/", data=payload, content_type="application/json")
        response = self.client.post("/subscription/activate/", data=payload, content_type="application/json")
        self.assertEqual(response.status_code, 409)

    def test_plan_catalog_is_seeded(self):
        response = self.client.get("/plans/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 3)
