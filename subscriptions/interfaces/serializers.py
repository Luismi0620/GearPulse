from rest_framework import serializers

from subscriptions.infra.models import PlanModel


class ActivateSubscriptionSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    plan = serializers.CharField()


class SubscriptionResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    plan = serializers.CharField()
    status = serializers.CharField()


class HealthMetricsResponseSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    pulse_bpm = serializers.IntegerField()
    sleep_hours = serializers.FloatField()
    training_load = serializers.IntegerField()
    generated_at = serializers.DateTimeField()


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanModel
        fields = ["name", "price", "duration_days"]
