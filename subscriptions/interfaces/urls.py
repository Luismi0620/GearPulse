from django.urls import path

from .views import ActivateSubscriptionView, HealthMetricsView, PlanListView

urlpatterns = [
    path("subscription/activate/", ActivateSubscriptionView.as_view(), name="activate"),
    path("subscription/<str:user_id>/metrics/", HealthMetricsView.as_view(), name="metrics"),
    path("plans/", PlanListView.as_view(), name="plan-list"),
]
