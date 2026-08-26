from devices.application.services import DeviceService, WorkoutService
from devices.infra.repositories import OrmDeviceRepository, OrmWorkoutSessionRepository

_device_repository = OrmDeviceRepository()
_session_repository = OrmWorkoutSessionRepository()


def get_device_service() -> DeviceService:
    return DeviceService(repository=_device_repository)


def get_workout_service() -> WorkoutService:
    return WorkoutService(
        device_repository=_device_repository,
        session_repository=_session_repository,
    )
