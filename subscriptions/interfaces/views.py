from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import ConflictError, NotFoundError
from subscriptions.dependencies import get_subscription_service
from subscriptions.infra.models import PlanModel
from subscriptions.interfaces.serializers import (
    ActivateSubscriptionSerializer,
    HealthMetricsResponseSerializer,
    PlanSerializer,
    SubscriptionResponseSerializer,
)


class ActivateSubscriptionView(APIView):
    def post(self, request):
        payload = ActivateSubscriptionSerializer(data=request.data)
        payload.is_valid(raise_exception=True)

        service = get_subscription_service()
        try:
            subscription = service.activate_subscription(**payload.validated_data)
        except NotFoundError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ConflictError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_409_CONFLICT)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "user_id": subscription.user_id,
            "plan": subscription.plan,
            "status": "active",
        }
        return Response(SubscriptionResponseSerializer(data).data, status=status.HTTP_201_CREATED)


class HealthMetricsView(APIView):
    def get(self, request, user_id: str):
        service = get_subscription_service()
        try:
            metrics = service.get_user_metrics(user_id)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        data = {
            "user_id": user_id,
            "pulse_bpm": metrics.pulse_bpm,
            "sleep_hours": metrics.sleep_hours,
            "training_load": metrics.training_load,
            "generated_at": metrics.generated_at,
        }
        return Response(HealthMetricsResponseSerializer(data).data, status=status.HTTP_200_OK)


class PlanListView(APIView):
    def get(self, request):
        plans = PlanModel.objects.all().order_by("duration_days")
        return Response(PlanSerializer(plans, many=True).data, status=status.HTTP_200_OK)
