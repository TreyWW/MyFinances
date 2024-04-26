from django.contrib import messages
from django.http import HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect

from backend.models import APIKey
from backend.types.htmx import HtmxHttpRequest


# Still working on


def generate_api_key(request: HtmxHttpRequest) -> HttpResponse:
    if not request.htmx:
        return redirect("user settings")
    if not request.user.is_staff or not request.user.is_superuser:
        messages.error(request, "You don't have permission to view this page.")
        return redirect("dashboard")

    service = request.POST.get("service")
    if not service:
        return HttpResponseBadRequest("Missing service")

    if service == "aws_api_destination":
        service = APIKey.ServiceTypes.AWS_API_DESTINATION
    else:
        return HttpResponseBadRequest("Invalid service")

    token = APIKey.objects.create(service=service)
    key = f"{token.id}:{token.key}"

    token.hash()

    return render(request, "pages/admin/api_keys/generate_response.html", {"key": key})
