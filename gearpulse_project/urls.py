from django.urls import include, path

urlpatterns = [
    path("", include("accounts.interfaces.urls")),
    path("", include("subscriptions.interfaces.urls")),
    path("", include("devices.interfaces.urls")),
]
