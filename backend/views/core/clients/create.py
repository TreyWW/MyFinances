from django.contrib import messages
from django.shortcuts import render, redirect

from backend.models import Client
from backend.types.htmx import HtmxHttpRequest
from backend.service.clients.create import create_client


def create_client_endpoint(request: HtmxHttpRequest):
    if request.method == "GET":
        return render(request, "pages/clients/create/create.html")

    client_or_error: Client | str = create_client(request)

    if isinstance(client_or_error, str):
        messages.error(request, client_or_error)
        return redirect("clients:create")

    if client_or_error:
        messages.success(request, f"Client created successfully (#{client_or_error.id})")
    else:
        messages.error(request, "Failed to create client - an unknown error occurred")
    return redirect("clients:dashboard")
