from typing import Literal

from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.service.clients.delete import delete_client
from backend.types.htmx import HtmxHttpRequest


@require_http_methods(["DELETE"])
def client_delete(request: HtmxHttpRequest, id: int):
    response: str | Literal[True] = delete_client(request, id)

    if isinstance(response, str):
        messages.error(request, response)
    else:
        messages.success(request, f"Successfully deleted client #{id}")
    return render(request, "base/toast.html")
