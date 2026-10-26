from django.http import JsonResponse
from django.shortcuts import render


def dashboard(request):
    """Render the bilingual UI; business requests are routed to Flask by Nginx."""
    return render(request, "dashboard.html")


def health(request):
    return JsonResponse({"status": "ok", "service": "django-ui"})
