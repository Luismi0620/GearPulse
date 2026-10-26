from django.test import Client, TestCase

from accounts.models import User
from common.exceptions import ConflictError, NotFoundError
from devices.application.services import DeviceService, WorkoutService
from devices.domain.builders import DeviceBuilder
from devices.infra.repositories import OrmDeviceRepository, OrmWorkoutSessionRepository


class DeviceBuilderTests(TestCase):
    def test_build_requires_all_fields(self):
        with self.assertRaises(ValueError):
            DeviceBuilder().for_user("u-1").build()

    def test_build_rejects_short_serial(self):
        with self.assertRaises(ValueError):
            (
                DeviceBuilder()
                .for_user("u-1")
                .with_brand("Garmin")
                .with_model("Fenix 7")
                .with_serial("AB1")
                .build()
            )

    def test_build_produces_valid_device(self):
        device = (
            DeviceBuilder()
            .for_user("u-1")
            .with_brand("Garmin")
            .with_model("Fenix 7")
            .with_serial("GAR-00123")
            .build()
        )
        self.assertTrue(device.active)
        self.assertEqual(device.serial_number, "GAR-00123")


class DeviceServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="device-owner@test.com")
        self.service = DeviceService(repository=OrmDeviceRepository())

    def test_pair_device_rejects_unknown_user(self):
        with self.assertRaises(NotFoundError):
            self.service.pair_device("00000000-0000-0000-0000-000000000000", "Garmin", "Fenix 7", "SN-000111")

    def test_pair_device_rejects_duplicate_serial(self):
        self.service.pair_device(str(self.user.id), "Garmin", "Fenix 7", "SN-000111")
        with self.assertRaises(ConflictError):
            self.service.pair_device(str(self.user.id), "Garmin", "Fenix 7", "SN-000111")


class WorkoutServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(email="workout-owner@test.com")
        self.device_service = DeviceService(repository=OrmDeviceRepository())
        self.device = self.device_service.pair_device(str(self.user.id), "Polar", "Vantage V3", "SN-000222")
        self.workout_service = WorkoutService(
            device_repository=OrmDeviceRepository(),
            session_repository=OrmWorkoutSessionRepository(),
        )

    def test_log_session_rejects_unknown_device(self):
        with self.assertRaises(NotFoundError):
            self.workout_service.log_session(
                "00000000-0000-0000-0000-000000000000",
                "2026-08-24T08:00:00Z",
                "2026-08-24T08:30:00Z",
                250,
                140,
            )

    def test_log_session_rejects_invalid_time_range(self):
        with self.assertRaises(ValueError):
            self.workout_service.log_session(
                self.device.id, "2026-08-24T08:30:00Z", "2026-08-24T08:00:00Z", 250, 140
            )


class StranglerBoundaryTests(TestCase):
    def test_legacy_device_route_is_no_longer_exposed_by_django(self):
        response = Client().post("/devices/pair/", data={}, content_type="application/json")
        self.assertEqual(response.status_code, 404)
