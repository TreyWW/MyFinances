from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http.response import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.core.service.clients.delete import delete_client, DeleteClientServiceResponse
from backend.core.service.clients.validate import validate_client
from backend.core.types.requests import WebRequest
from backend.clients.models import Client


@require_http_methods(["GET"])
@web_require_scopes("clients:read", False, False, "clients:dashboard")
def client_detail_endpoint(request: WebRequest, id):
    try:
        client = validate_client(request, id)
    except (ValidationError, Client.DoesNotExist):
        messages.error(request, "This client does not exist")
        return redirect("clients:dashboard")

    return render(request, "pages/clients/detail/dashboard.html", {"client": client})


@require_http_methods(["DELETE"])
@web_require_scopes("clients:write", False, False, "clients:dashboard")
def delete_client_endpoint(request: WebRequest, id) -> HttpResponse:
    delete_response: DeleteClientServiceResponse = delete_client(request, id)

    if delete_response.failed:
        messages.error(request, delete_response.error)
    else:
        messages.success(request, f"Successfully deleted client #{id}")

    if request.htmx:
        http_response = HttpResponse(status=301)
        http_response["HX-Redirect"] = "/dashboard/clients/"
        return http_response
    return redirect("clients:dashboard")
