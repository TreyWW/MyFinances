from backend.core.types.requests import WebRequest
from django.shortcuts import render


def view_reports_endpoint(request: WebRequest):
    return render(request, "pages/reports/dashboard.html")
