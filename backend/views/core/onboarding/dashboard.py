from django.shortcuts import render

from backend.types.requests import WebRequest


def dashboard(request: WebRequest):
    return render(request, "pages/onboarding/dashboard/dashboard.html")
