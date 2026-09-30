from django.shortcuts import render


def dashboard(request):
    """Render the temporary browser interface for the GearPulse API."""
    return render(request, "dashboard.html")
