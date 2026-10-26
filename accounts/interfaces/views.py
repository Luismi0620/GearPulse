from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.application.services import UserService
from accounts.interfaces.serializers import RegisterUserSerializer, UserSerializer
from common.exceptions import ConflictError


class RegisterUserView(APIView):
    def post(self, request):
        payload = RegisterUserSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        service = UserService()
        try:
            user = service.register_user(
                payload.validated_data["email"],
                payload.validated_data.get("role", ""),
            )
        except ConflictError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
