from django.shortcuts import render

from backend.types.requests import WebRequest


def billing_dashboard_endpoint(request: WebRequest):
    return render(request, "pages/billing/dashboard.html")
