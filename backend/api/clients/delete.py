from typing import Literal

from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.service.clients.delete import delete_client
from backend.types.requests import WebRequest


@require_http_methods(["DELETE"])
@web_require_scopes("clients:write")
def client_delete(request: WebRequest, id: int):
    response: str | Literal[True] = delete_client(request, id)

    if isinstance(response, str):
        messages.error(request, response)
    else:
        messages.success(request, f"Successfully deleted client #{id}")
    return render(request, "base/toast.html")
