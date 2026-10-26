import unittest

from services.async_service.app import create_app


class AsyncApiTests(unittest.TestCase):
    def setUp(self):
        self.client = create_app(
            {
                "TESTING": True,
                "CELERY": {
                    "broker_url": "memory://",
                    "result_backend": "cache+memory://",
                    "task_always_eager": True,
                    "task_store_eager_result": True,
                },
            }
        ).test_client()

    def test_subscription_notification_is_queued(self):
        response = self.client.post(
            "/api/v2/notifications/subscription-activated/",
            json={"user_id": "user-1", "plan": "monthly"},
        )
        self.assertEqual(response.status_code, 202)
        status = self.client.get(f"/api/v2/tasks/{response.json['task_id']}/")
        self.assertEqual(status.json["status"], "success")

    def test_workout_report_is_generated(self):
        response = self.client.post(
            "/api/v2/reports/workout/",
            json={"id": "workout-1", "duration_minutes": 40, "calories": 400},
        )
        self.assertEqual(response.status_code, 202)
        status = self.client.get(f"/api/v2/tasks/{response.json['task_id']}/")
        self.assertEqual(status.json["result"]["calories_per_minute"], 10.0)

    def test_invalid_event_is_rejected(self):
        response = self.client.post("/api/v2/reports/workout/", json={})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
