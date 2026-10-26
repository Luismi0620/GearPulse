import uuid

from django.core.exceptions import ValidationError
from django.db import models


class User(models.Model):
    class Role(models.TextChoices):
        ATHLETE = "athlete", "Athlete"
        ADMIN = "admin", "Admin"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ATHLETE)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self) -> None:
        if not self.email or "@" not in self.email:
            raise ValidationError("A valid email is required")

    def __str__(self) -> str:
        return f"{self.email} ({self.role})"
