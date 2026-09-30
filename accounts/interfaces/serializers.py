from rest_framework import serializers

from accounts.models import User


class RegisterUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=User.Role.choices, required=False)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "role", "created_at"]
