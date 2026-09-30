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

    def test_metrics_endpoint_accepts_json(self):
        response = self.client.post(
            "/api/v2/health-metrics/",
            json={"user_id": "user-123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["user_id"], "user-123")

    def test_metrics_endpoint_rejects_invalid_json_payload(self):
        response = self.client.post("/api/v2/health-metrics/", json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error"], "user_id is required")
        self.assertEqual(response.json["status"], 400)

    def test_unknown_route_returns_structured_404(self):
        response = self.client.get("/missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["status"], 404)

    def test_unexpected_errors_return_structured_500(self):
        app = create_app()

        @app.get("/_test/error")
        def raise_error():
            raise RuntimeError("simulated failure")

        with self.assertLogs(app.logger.name, level="ERROR"):
            response = app.test_client().get("/_test/error")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "internal server error", "status": 500})


if __name__ == "__main__":
    unittest.main()
