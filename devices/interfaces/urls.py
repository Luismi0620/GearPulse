from django.urls import path

from devices.interfaces.views import PairDeviceView, WorkoutSessionListCreateView

urlpatterns = [
    path("devices/pair/", PairDeviceView.as_view(), name="pair-device"),
    path("devices/<str:device_id>/workouts/", WorkoutSessionListCreateView.as_view(), name="device-workouts"),
]
