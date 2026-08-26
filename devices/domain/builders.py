import uuid

from django.utils import timezone

from .entities import Device

MIN_SERIAL_LENGTH = 6


class DeviceBuilder:
    """
    Builder for the most complex entity in the system: Device.

    A device is only valid once it has an owner, a brand, a model and a
    serial number that follows the manufacturer format. The fluent
    interface lets the service layer assemble it step by step while this
    class is the single place that guarantees the object is well-formed
    before it is ever persisted.
    """

    def __init__(self) -> None:
        self._user_id: str | None = None
        self._brand: str | None = None
        self._model: str | None = None
        self._serial_number: str | None = None

    def for_user(self, user_id: str) -> "DeviceBuilder":
        self._user_id = user_id.strip() if user_id else ""
        return self

    def with_brand(self, brand: str) -> "DeviceBuilder":
        self._brand = brand.strip() if brand else ""
        return self

    def with_model(self, model: str) -> "DeviceBuilder":
        self._model = model.strip() if model else ""
        return self

    def with_serial(self, serial_number: str) -> "DeviceBuilder":
        self._serial_number = serial_number.strip().upper() if serial_number else ""
        return self

    def build(self) -> Device:
        if not self._user_id:
            raise ValueError("user_id is required")
        if not self._brand:
            raise ValueError("brand is required")
        if not self._model:
            raise ValueError("model is required")
        if not self._serial_number or len(self._serial_number) < MIN_SERIAL_LENGTH:
            raise ValueError(f"serial_number must have at least {MIN_SERIAL_LENGTH} characters")

        return Device(
            id=str(uuid.uuid4()),
            user_id=self._user_id,
            brand=self._brand,
            model=self._model,
            serial_number=self._serial_number,
            paired_at=timezone.now(),
            active=True,
        )
