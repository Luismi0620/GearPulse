import unittest

from flask_metrics_service.app import create_app


class HealthMetricsApiTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app().test_client()

    def test_health_check_returns_json(self):
        response = self.client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["service"], "health-metrics")

    def test_metrics_endpoint_returns_expected_json_contract(self):
        response = self.client.get("/api/v2/health-metrics/user-123/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["user_id"], "user-123")
        self.assertIn("pulse_bpm", response.json)
        self.assertIn("generated_at", response.json)
        self.assertEqual(response.json["source"], "flask-health-metrics-service")

    def test_unknown_route_returns_structured_404(self):
        response = self.client.get("/missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["status"], 404)


if __name__ == "__main__":
    unittest.main()
