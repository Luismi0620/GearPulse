import unittest

from services.accounts_service.app import create_app, db


class AccountsApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite://"})
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_register_and_read_user(self):
        created = self.client.post(
            "/api/v2/users/register/", json={"email": "ana@example.com", "role": "athlete"}
        )
        self.assertEqual(created.status_code, 201)
        loaded = self.client.get(f"/api/v2/users/{created.json['id']}/")
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(loaded.json["email"], "ana@example.com")

    def test_duplicate_email_returns_conflict(self):
        payload = {"email": "ana@example.com"}
        self.client.post("/api/v2/users/register/", json=payload)
        response = self.client.post("/api/v2/users/register/", json=payload)
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json["error"]["code"], "email_conflict")

    def test_invalid_payload_is_rejected(self):
        response = self.client.post("/api/v2/users/register/", json={"email": "invalid"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
