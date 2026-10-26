from django.urls import include, path

from gearpulse_project.views import dashboard, health

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("health/", health, name="health"),
    path("i18n/", include("django.conf.urls.i18n")),
]
