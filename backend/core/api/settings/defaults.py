from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.clients.models import Client
from backend.core.service.clients.validate import validate_client
from backend.core.service.defaults.get import get_account_defaults
from backend.core.service.defaults.update import change_client_defaults
from backend.core.types.requests import WebRequest


# @require_http_methods(["GET", "PUT"])
@require_http_methods(["GET", "POST"])
def handle_client_defaults_endpoints(request: WebRequest, client_id: int | None = None):
    if request.method == "GET":
        return get_defaults_endpoint(request, client_id)
    # elif request.method == "PUT":
    elif request.method == "POST":
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

        defaults = get_account_defaults(request.actor, client)
        context |= {"client": client}
    else:
        defaults = get_account_defaults(request.actor)

    return render(request, "pages/clients/detail/client_defaults.html", context | {"defaults": defaults})


# @require_http_methods(["PUT"])
@require_http_methods(["POST"])
def change_client_defaults_endpoint(request: WebRequest, client_id: int | None = None):
    context: dict = {}

    if client_id:
        try:
            client = validate_client(request, client_id, get_defaults=True)
        except (ValidationError, Client.DoesNotExist):
            return HttpResponse("Something went wrong")

        defaults = get_account_defaults(request.actor, client)
        context |= {"client": client}
    else:
        defaults = get_account_defaults(request.actor)

    response = change_client_defaults(request, defaults)

    if response.failed:
        messages.error(request, response.error)
        return render(request, "base/toast.html")

    messages.success(request, "Successfully updated client defaults")
    return render(request, "base/toast.html")


@require_http_methods(["DELETE"])
def remove_client_default_logo_endpoint(request: WebRequest, client_id: int | None = None):
    context: dict = {}

    if client_id:
        try:
            client = validate_client(request, client_id, get_defaults=True)
        except (ValidationError, Client.DoesNotExist):
            return HttpResponse("Something went wrong")

        defaults = get_account_defaults(request.actor, client)
        context |= {"client": client}
    else:
        defaults = get_account_defaults(request.actor)

    if not defaults.default_invoice_logo:
        messages.error(request, "No default logo to remove")
        return render(request, "base/toast.html")

    defaults.default_invoice_logo.delete()

    messages.success(request, "Successfully updated client defaults")
    resp = render(request, "base/toast.html")
    resp["HX-Refresh"] = "true"
    return resp
