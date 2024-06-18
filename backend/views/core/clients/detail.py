from typing import Literal

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.service.clients.delete import delete_client
from backend.service.clients.validate import validate_client
from backend.types.htmx import HtmxHttpRequest
from backend.models import Client, ClientDefaults, User
from backend.service.clients.detail import change_client_defaults


@require_http_methods(["GET", "PUT"])
def handle_client_defaults_endpoints(request: HtmxHttpRequest, id):
    if request.method == "GET":
        return get_client_defaults_endpoint(request, id)
    elif request.method == "PUT":
        return change_client_defaults_endpoint(request, id)
    else:
        return HttpResponse("Something went wrong")


@require_http_methods(["GET"])
def client_detail_endpoint(request: HtmxHttpRequest, id):
    try:
        client = validate_client(request, id)
    except (ValidationError, Client.DoesNotExist):
        messages.error(request, "This client does not exist")
        return redirect("clients:dashboard")

    return render(request, "pages/clients/detail/dashboard.html", {"client": client})

@require_http_methods(["GET"])
def get_client_defaults_endpoint(request: HtmxHttpRequest, id):
    try:
        client = validate_client(request, id, get_defaults=True)
    except (ValidationError, Client.DoesNotExist):
        return HttpResponse("Something went wrong")

    defaults: ClientDefaults = (
        client.client_defaults if hasattr(client, "client_defaults") else ClientDefaults.objects.create(client=client)
    )

    return render(request, "pages/clients/detail/client_defaults.html", {"defaults": defaults, "client": client})


@require_http_methods(["PUT"])
def change_client_defaults_endpoint(request: HtmxHttpRequest, id):
    try:
        client = validate_client(request, id, get_defaults=True)
    except (ValidationError, Client.DoesNotExist):
        return HttpResponse("Something went wrong")

    defaults: ClientDefaults = (
        client.client_defaults if hasattr(client, "client_defaults") else ClientDefaults.objects.create(client=client)
    )

    response: str | None = change_client_defaults(request, client, defaults)

    if response:
        messages.error(request, response)
        return render(request, "base/toast.html")

    messages.success(request, "Successfully updated client defaults")
    return render(request, "base/toast.html")

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
