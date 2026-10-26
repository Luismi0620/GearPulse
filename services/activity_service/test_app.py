import unittest

from services.activity_service.app import create_app, db


class ActivityApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": "sqlite://",
                "ACCOUNT_VALIDATOR": lambda user_id: user_id == "known-user",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def _pair(self):
        return self.client.post(
            "/api/v2/devices/pair/",
            json={"user_id": "known-user", "brand": "Garmin", "model": "Fenix", "serial_number": "GP-0001"},
        )

    def test_pair_and_log_workout(self):
        paired = self._pair()
        self.assertEqual(paired.status_code, 201)
        response = self.client.post(
            f"/api/v2/devices/{paired.json['id']}/workouts/",
            json={
                "start_time": "2026-09-01T10:00:00Z",
                "end_time": "2026-09-01T10:45:00Z",
                "calories": 420,
                "avg_heart_rate": 138,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["duration_minutes"], 45.0)

    def test_duplicate_serial_returns_conflict(self):
        self._pair()
        self.assertEqual(self._pair().status_code, 409)

    def test_unknown_user_is_rejected(self):
        response = self.client.post(
            "/api/v2/devices/pair/",
            json={"user_id": "missing", "brand": "Polar", "model": "V3", "serial_number": "GP-0002"},
        )
        self.assertEqual(response.status_code, 404)

    def test_invalid_time_range_is_rejected(self):
        device_id = self._pair().json["id"]
        response = self.client.post(
            f"/api/v2/devices/{device_id}/workouts/",
            json={
                "start_time": "2026-09-01T11:00:00Z",
                "end_time": "2026-09-01T10:00:00Z",
                "calories": 10,
                "avg_heart_rate": 80,
            },
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
