from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from core.decorators import web_require_scopes
from backend.finance.service.clients.delete import delete_client, DeleteClientServiceResponse
from core.types.requests import WebRequest


@require_http_methods(["DELETE"])
@web_require_scopes("clients:write")
def client_delete(request: WebRequest, id: int):
    response: DeleteClientServiceResponse = delete_client(request, id)

    if response.failed:
        messages.error(request, response.error)
    else:
        messages.success(request, f"Successfully deleted client #{id}")
    return render(request, "core/base/toast.html")
