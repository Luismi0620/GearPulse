from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import ConflictError, NotFoundError
from devices.dependencies import get_device_service, get_workout_service
from devices.interfaces.serializers import (
    DeviceResponseSerializer,
    LogWorkoutSessionSerializer,
    PairDeviceSerializer,
    WorkoutSessionResponseSerializer,
)


class PairDeviceView(APIView):
    def post(self, request):
        payload = PairDeviceSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        service = get_device_service()
        try:
            device = service.pair_device(**payload.validated_data)
        except NotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ConflictError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            DeviceResponseSerializer(device.__dict__).data,
            status=status.HTTP_201_CREATED,
        )


class WorkoutSessionListCreateView(APIView):
    def post(self, request, device_id: str):
        payload = LogWorkoutSessionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        service = get_workout_service()
        try:
            session = service.log_session(device_id=device_id, **payload.validated_data)
        except NotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        data = {**session.__dict__, "duration_minutes": session.duration_minutes()}
        return Response(WorkoutSessionResponseSerializer(data).data, status=status.HTTP_201_CREATED)

    def get(self, request, device_id: str):
        service = get_workout_service()
        try:
            sessions = service.list_sessions(device_id)
        except NotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        data = [{**s.__dict__, "duration_minutes": s.duration_minutes()} for s in sessions]
        return Response(WorkoutSessionResponseSerializer(data, many=True).data, status=status.HTTP_200_OK)
