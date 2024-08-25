from django.shortcuts import render

from backend.types.requests import WebRequest


def file_storage_dashboard_endpoint(request: WebRequest):
    return render(request, "pages/file_storage/dashboard.html")
