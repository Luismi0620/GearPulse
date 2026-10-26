import unittest

from services.subscriptions_service.app import create_app, db


class SubscriptionsApiTests(unittest.TestCase):
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

    def test_seeded_plan_catalog(self):
        response = self.client.get("/api/v2/plans/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

    def test_activate_and_check_subscription(self):
        response = self.client.post(
            "/api/v2/subscriptions/activate/", json={"user_id": "known-user", "plan": "monthly"}
        )
        self.assertEqual(response.status_code, 201)
        active = self.client.get("/internal/subscriptions/known-user/active/")
        self.assertTrue(active.json["active"])

    def test_unknown_user_is_rejected(self):
        response = self.client.post(
            "/api/v2/subscriptions/activate/", json={"user_id": "missing", "plan": "monthly"}
        )
        self.assertEqual(response.status_code, 404)

    def test_duplicate_subscription_returns_conflict(self):
        payload = {"user_id": "known-user", "plan": "monthly"}
        self.client.post("/api/v2/subscriptions/activate/", json=payload)
        response = self.client.post("/api/v2/subscriptions/activate/", json=payload)
        self.assertEqual(response.status_code, 409)


if __name__ == "__main__":
    unittest.main()
