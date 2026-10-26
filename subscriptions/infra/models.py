from django.db import models

from accounts.models import User


class PlanModel(models.Model):
    """Catalog of subscription plans. Read model used to list pricing/options."""

    name = models.CharField(max_length=20, primary_key=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.PositiveIntegerField()

    class Meta:
        db_table = "subscriptions_plan"

    def __str__(self) -> str:
        return f"{self.name} (${self.price}/{self.duration_days}d)"


class SubscriptionModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="subscription")
    plan = models.CharField(max_length=20)
    started_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "subscriptions_subscription"
