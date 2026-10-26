import uuid

from django.db import models

from accounts.models import User


class DeviceModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="devices")
    brand = models.CharField(max_length=80)
    model_name = models.CharField(max_length=80)
    serial_number = models.CharField(max_length=64, unique=True)
    paired_at = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "devices_device"


class WorkoutSessionModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(DeviceModel, on_delete=models.CASCADE, related_name="workout_sessions")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    calories = models.PositiveIntegerField()
    avg_heart_rate = models.PositiveIntegerField()

    class Meta:
        db_table = "devices_workoutsession"
