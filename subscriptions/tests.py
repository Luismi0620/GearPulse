import json

from django.test import Client, SimpleTestCase

from subscriptions.application.services import SubscriptionService
from subscriptions.infra.metrics_provider import SimulatedMetricsProvider
from subscriptions.infra.notifiers import MockNotifier
from subscriptions.infra.repositories import InMemorySubscriptionRepository


class SubscriptionServiceTests(SimpleTestCase):
    def setUp(self):
        self.repository = InMemorySubscriptionRepository()
        self.service = SubscriptionService(
            repository=self.repository,
            notifier=MockNotifier(),
            metrics_provider=SimulatedMetricsProvider(),
        )

    def test_activate_subscription_creates_active_record(self):
        subscription = self.service.activate_subscription("u-123", "monthly")
        self.assertEqual(subscription.user_id, "u-123")
        self.assertTrue(subscription.is_active())

    def test_get_metrics_requires_active_subscription(self):
        with self.assertRaises(ValueError):
            self.service.get_user_metrics("u-without-plan")


class SubscriptionViewsTests(SimpleTestCase):
    def setUp(self):
        self.client = Client()

    def test_activate_then_get_metrics(self):
        activate_response = self.client.post(
            "/subscription/activate/",
            data=json.dumps({"user_id": "u-99", "plan": "monthly"}),
            content_type="application/json",
        )
        self.assertEqual(activate_response.status_code, 201)

        metrics_response = self.client.get("/subscription/u-99/metrics/")
        self.assertEqual(metrics_response.status_code, 200)

    def test_metrics_without_subscription_returns_403(self):
        metrics_response = self.client.get("/subscription/no-sub/metrics/")
        self.assertEqual(metrics_response.status_code, 403)
