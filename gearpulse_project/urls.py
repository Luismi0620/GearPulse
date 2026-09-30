from django.urls import include, path

from gearpulse_project.views import dashboard

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("", include("accounts.interfaces.urls")),
    path("", include("subscriptions.interfaces.urls")),
    path("", include("devices.interfaces.urls")),
]
