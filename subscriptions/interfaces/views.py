import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from subscriptions.dependencies import get_subscription_service


def _request_payload(request) -> dict:
    if request.content_type == "application/json":
        return json.loads(request.body or "{}")
    return request.POST.dict()


@method_decorator(csrf_exempt, name="dispatch")
class ActivateSubscriptionView(View):
    def post(self, request):
        data = _request_payload(request)
        service = get_subscription_service()
        try:
            subscription = service.activate_subscription(data.get("user_id", ""), data.get("plan", ""))
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=400)
        return JsonResponse({"user_id": subscription.user_id, "plan": subscription.plan, "status": "active"}, status=201)


@method_decorator(csrf_exempt, name="dispatch")
class HealthMetricsView(View):
    def get(self, request, user_id: str):
        service = get_subscription_service()
        try:
            metrics = service.get_user_metrics(user_id)
        except ValueError as exc:
            return JsonResponse({"error": str(exc)}, status=403)
        return JsonResponse(
            {
                "user_id": user_id,
                "pulse_bpm": metrics.pulse_bpm,
                "sleep_hours": metrics.sleep_hours,
                "training_load": metrics.training_load,
                "generated_at": metrics.generated_at.isoformat(),
            }
        )
