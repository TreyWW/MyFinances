from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Client
from backend.service.clients.validate import validate_client
from backend.service.defaults.get import get_account_defaults
from backend.service.defaults.update import change_client_defaults
from backend.types.requests import WebRequest


@require_http_methods(["GET", "PUT"])
def handle_client_defaults_endpoints(request: WebRequest, client_id: int | None = None):
    if request.method == "GET":
        return get_defaults_endpoint(request, client_id)
    elif request.method == "PUT":
        return change_client_defaults_endpoint(request, client_id)
    else:
        return HttpResponse("Something went wrong")


@require_http_methods(["GET"])
def get_defaults_endpoint(request: WebRequest, client_id: int | None = None):
    context: dict = {}

    if client_id:
        try:
            client = validate_client(request, client_id, get_defaults=True)
        except (ValidationError, Client.DoesNotExist):
            return HttpResponse("Something went wrong")

        defaults = get_account_defaults(request, client)
        context |= {"client": client}
    else:
        defaults = get_account_defaults(request)

    return render(request, "pages/clients/detail/client_defaults.html", context | {"defaults": defaults})


@require_http_methods(["PUT"])
def change_client_defaults_endpoint(request: WebRequest, client_id: int | None = None):
    context: dict = {}

    if client_id:
        try:
            client = validate_client(request, client_id, get_defaults=True)
        except (ValidationError, Client.DoesNotExist):
            return HttpResponse("Something went wrong")

        defaults = get_account_defaults(request, client)
        context |= {"client": client}
    else:
        defaults = get_account_defaults(request)

    response = change_client_defaults(request, defaults)

    if response.failed:
        messages.error(request, response.error)
        return render(request, "base/toast.html")

    messages.success(request, "Successfully updated client defaults")
    return render(request, "base/toast.html")
