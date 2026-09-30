from rest_framework import serializers


class PairDeviceSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    serial_number = serializers.CharField()


class DeviceResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    user_id = serializers.CharField()
    brand = serializers.CharField()
    model = serializers.CharField()
    serial_number = serializers.CharField()
    paired_at = serializers.DateTimeField()
    active = serializers.BooleanField()


class LogWorkoutSessionSerializer(serializers.Serializer):
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    calories = serializers.IntegerField(min_value=0)
    avg_heart_rate = serializers.IntegerField(min_value=1)


class WorkoutSessionResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    device_id = serializers.CharField()
    start_time = serializers.DateTimeField()
    end_time = serializers.DateTimeField()
    calories = serializers.IntegerField()
    avg_heart_rate = serializers.IntegerField()
    duration_minutes = serializers.FloatField()
