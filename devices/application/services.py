import uuid
from datetime import datetime

from django.core.exceptions import ValidationError

from accounts.models import User
from common.exceptions import ConflictError, NotFoundError
from devices.domain.builders import DeviceBuilder
from devices.domain.entities import Device, WorkoutSession
from devices.domain.ports import DeviceRepository, WorkoutSessionRepository


class DeviceService:
    def __init__(self, repository: DeviceRepository) -> None:
        self._repository = repository

    def pair_device(self, user_id: str, brand: str, model: str, serial_number: str) -> Device:
        try:
            user_exists = User.objects.filter(id=user_id).exists()
        except ValidationError:
            user_exists = False
        if not user_exists:
            raise NotFoundError(f"user '{user_id}' does not exist")

        existing = self._repository.find_active_by_serial(serial_number)
        if existing is not None:
            raise ConflictError(f"device with serial '{serial_number}' is already paired")

        device = (
            DeviceBuilder()
            .for_user(user_id)
            .with_brand(brand)
            .with_model(model)
            .with_serial(serial_number)
            .build()
        )
        self._repository.save(device)
        return device


class WorkoutService:
    def __init__(self, device_repository: DeviceRepository, session_repository: WorkoutSessionRepository) -> None:
        self._device_repository = device_repository
        self._session_repository = session_repository

    def log_session(
        self,
        device_id: str,
        start_time: datetime,
        end_time: datetime,
        calories: int,
        avg_heart_rate: int,
    ) -> WorkoutSession:
        device = self._device_repository.find_by_id(device_id)
        if device is None:
            raise NotFoundError(f"device '{device_id}' does not exist")
        if end_time <= start_time:
            raise ValueError("end_time must be after start_time")
        if calories < 0 or avg_heart_rate <= 0:
            raise ValueError("calories and avg_heart_rate must be positive")

        session = WorkoutSession(
            id=str(uuid.uuid4()),
            device_id=device_id,
            start_time=start_time,
            end_time=end_time,
            calories=calories,
            avg_heart_rate=avg_heart_rate,
        )
        self._session_repository.save(session)
        return session

    def list_sessions(self, device_id: str) -> list[WorkoutSession]:
        if self._device_repository.find_by_id(device_id) is None:
            raise NotFoundError(f"device '{device_id}' does not exist")
        return self._session_repository.list_by_device(device_id)
