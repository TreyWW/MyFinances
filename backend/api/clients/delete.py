from typing import Literal

from django.contrib import messages
from django.http.response import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from backend.models import Client
from backend.service.clients.delete import delete_client
from backend.types.htmx import HtmxHttpRequest


@require_http_methods(["DELETE"])
@login_required
def client_delete(request: HtmxHttpRequest, id: int):
    response: str | Literal[True] = delete_client(request, id)

    if isinstance(response, str):
        messages.error(request, response)
    else:
        messages.success(request, f"Successfully deleted client #{id}")

    return render(request, "base/toast.html")
