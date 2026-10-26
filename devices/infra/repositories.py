from django.core.exceptions import ValidationError

from devices.domain.entities import Device, WorkoutSession
from devices.domain.ports import DeviceRepository, WorkoutSessionRepository

from .models import DeviceModel, WorkoutSessionModel


def _to_device_entity(row: DeviceModel) -> Device:
    return Device(
        id=str(row.id),
        user_id=str(row.user_id),
        brand=row.brand,
        model=row.model_name,
        serial_number=row.serial_number,
        paired_at=row.paired_at,
        active=row.active,
    )


def _to_session_entity(row: WorkoutSessionModel) -> WorkoutSession:
    return WorkoutSession(
        id=str(row.id),
        device_id=str(row.device_id),
        start_time=row.start_time,
        end_time=row.end_time,
        calories=row.calories,
        avg_heart_rate=row.avg_heart_rate,
    )


class OrmDeviceRepository(DeviceRepository):
    def save(self, device: Device) -> None:
        DeviceModel.objects.update_or_create(
            id=device.id,
            defaults={
                "user_id": device.user_id,
                "brand": device.brand,
                "model_name": device.model,
                "serial_number": device.serial_number,
                "paired_at": device.paired_at,
                "active": device.active,
            },
        )

    def find_by_id(self, device_id: str) -> Device | None:
        try:
            row = DeviceModel.objects.filter(id=device_id).first()
        except ValidationError:
            return None
        return _to_device_entity(row) if row else None

    def find_active_by_serial(self, serial_number: str) -> Device | None:
        row = DeviceModel.objects.filter(serial_number=serial_number.upper(), active=True).first()
        return _to_device_entity(row) if row else None


class OrmWorkoutSessionRepository(WorkoutSessionRepository):
    def save(self, session: WorkoutSession) -> None:
        WorkoutSessionModel.objects.update_or_create(
            id=session.id,
            defaults={
                "device_id": session.device_id,
                "start_time": session.start_time,
                "end_time": session.end_time,
                "calories": session.calories,
                "avg_heart_rate": session.avg_heart_rate,
            },
        )

    def list_by_device(self, device_id: str) -> list[WorkoutSession]:
        rows = WorkoutSessionModel.objects.filter(device_id=device_id).order_by("start_time")
        return [_to_session_entity(row) for row in rows]
