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


class StranglerBoundaryTests(TestCase):
    def test_legacy_user_route_is_no_longer_exposed_by_django(self):
        response = Client().post("/users/register/", data={}, content_type="application/json")
        self.assertEqual(response.status_code, 404)
