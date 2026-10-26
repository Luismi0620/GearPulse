import unittest

from services.integration_service.adapters import IntegrationUnavailable
from services.integration_service.app import create_app


class FakeWeatherAdapter:
    def current_conditions(self, latitude, longitude):
        return {"provider": "fake", "latitude": latitude, "longitude": longitude, "temperature_c": 22}


class FakeAllyAdapter:
    def fetch_summary(self):
        return {"source": "allied-team", "status": "available", "data": {"score": 90}}


class FailingAllyAdapter:
    def fetch_summary(self):
        raise IntegrationUnavailable("offline")


class IntegrationApiTests(unittest.TestCase):
    def test_third_party_adapter_contract(self):
        client = create_app({"TESTING": True, "WEATHER_ADAPTER": FakeWeatherAdapter()}).test_client()
        response = client.get("/api/v2/integrations/weather/?latitude=6.2&longitude=-75.5")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["provider"], "fake")

    def test_ally_contract_is_normalized(self):
        client = create_app({"TESTING": True, "ALLY_ADAPTER": FakeAllyAdapter()}).test_client()
        response = client.get("/api/v2/integrations/ally/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["source"], "allied-team")

    def test_ally_failure_is_resilient(self):
        client = create_app({"TESTING": True, "ALLY_ADAPTER": FailingAllyAdapter()}).test_client()
        response = client.get("/api/v2/integrations/ally/")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json["error"]["code"], "ally_unavailable")

    def test_public_service_contract(self):
        response = create_app({"TESTING": True}).test_client().get("/api/v2/public/summary/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("health-metrics", response.json["capabilities"])


if __name__ == "__main__":
    unittest.main()
