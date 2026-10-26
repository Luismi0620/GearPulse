from abc import ABC, abstractmethod

from .entities import Device, WorkoutSession


class DeviceRepository(ABC):
    @abstractmethod
    def save(self, device: Device) -> None:
        raise NotImplementedError

    @abstractmethod
    def find_by_id(self, device_id: str) -> Device | None:
        raise NotImplementedError

    @abstractmethod
    def find_active_by_serial(self, serial_number: str) -> Device | None:
        raise NotImplementedError


class WorkoutSessionRepository(ABC):
    @abstractmethod
    def save(self, session: WorkoutSession) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_device(self, device_id: str) -> list[WorkoutSession]:
        raise NotImplementedError
