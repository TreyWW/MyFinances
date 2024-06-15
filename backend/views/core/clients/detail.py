from typing import Literal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.service.clients.delete import delete_client
from backend.service.clients.validate import validate_client
from backend.types.htmx import HtmxHttpRequest
from backend.models import Client


@require_http_methods(["GET"])
def client_detail_endpoint(request: HtmxHttpRequest, id):
    try:
        client = validate_client(request, id)
    except (ValidationError, Client.DoesNotExist):
        messages.error(request, "This client does not exist")
        return redirect("clients:dashboard")

    return render(request, "pages/clients/detail/dashboard.html", {"client": client})


@require_http_methods(["DELETE"])
def delete_client_endpoint(request: HtmxHttpRequest, id) -> HttpResponse:
    response: str | Literal[True] = delete_client(request, id)

    if isinstance(response, str):
        messages.error(request, f"Failed to delete the client {id}: {response}")
    else:
        messages.success(request, f"Successfully deleted client #{id}")

    if request.htmx:
        http_response = HttpResponse(status=301)
        http_response["HX-Redirect"] = "/dashboard/clients/"
        return http_response
    return redirect("clients:dashboard")
