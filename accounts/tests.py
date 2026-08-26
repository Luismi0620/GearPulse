from django.test import Client, TestCase

from accounts.application.services import UserService
from accounts.models import User
from common.exceptions import ConflictError


class UserServiceTests(TestCase):
    def test_register_user_creates_record(self):
        user = UserService().register_user("athlete@test.com", "athlete")
        self.assertEqual(user.email, "athlete@test.com")

    def test_register_user_rejects_invalid_email(self):
        with self.assertRaises(ValueError):
            UserService().register_user("not-an-email", "athlete")

    def test_register_user_rejects_duplicate_email(self):
        UserService().register_user("dup@test.com", "athlete")
        with self.assertRaises(ConflictError):
            UserService().register_user("dup@test.com", "athlete")


class RegisterUserViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_register_returns_201(self):
        response = self.client.post(
            "/users/register/",
            data={"email": "new@test.com", "role": "athlete"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

    def test_register_duplicate_returns_409(self):
        self.client.post(
            "/users/register/",
            data={"email": "twice@test.com"},
            content_type="application/json",
        )
        response = self.client.post(
            "/users/register/",
            data={"email": "twice@test.com"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 409)

    def test_register_invalid_payload_returns_400(self):
        response = self.client.post("/users/register/", data={}, content_type="application/json")
        self.assertEqual(response.status_code, 400)
