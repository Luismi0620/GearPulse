from django.urls import path

from accounts.interfaces.views import RegisterUserView

urlpatterns = [
    path("users/register/", RegisterUserView.as_view(), name="register-user"),
]
