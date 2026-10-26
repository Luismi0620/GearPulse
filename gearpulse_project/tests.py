from django.test import Client, TestCase, override_settings


class PresentationLayerTests(TestCase):
    def test_health_check_is_json(self):
        response = Client().get("/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["service"], "django-ui")

    def test_dashboard_uses_microservice_routes(self):
        response = Client().get("/")
        self.assertContains(response, "/api/v2/users/register/")
        self.assertNotContains(response, "'/users/register/'")

    @override_settings(LANGUAGE_CODE="en")
    def test_dashboard_exposes_english_language_option(self):
        response = Client(HTTP_ACCEPT_LANGUAGE="en").get("/")
        self.assertContains(response, 'value="en"')
