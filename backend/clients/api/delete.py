from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.core.service.clients.delete import delete_client, DeleteClientServiceResponse
from backend.core.types.requests import WebRequest


@require_http_methods(["DELETE"])
@web_require_scopes("clients:write")
def client_delete(request: WebRequest, id: int):
    response: DeleteClientServiceResponse = delete_client(request, id)

    if response.failed:
        messages.error(request, response.error)
    else:
        messages.success(request, f"Successfully deleted client #{id}")
    return render(request, "base/toast.html")
