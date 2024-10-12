from django.contrib import messages
from django.shortcuts import render, redirect

from backend.decorators import web_require_scopes
from backend.core.service.clients.create import create_client, CreateClientServiceResponse
from backend.core.types.requests import WebRequest


@web_require_scopes("clients:write", False, False, "clients:dashboard")
def create_client_endpoint(request: WebRequest):
    if request.method == "GET":
        return render(request, "pages/clients/create/create.html")

    client_response: CreateClientServiceResponse = create_client(request)

    if client_response.failed:
        messages.error(request, client_response.error)
        return redirect("clients:create")

    messages.success(request, f"Client created successfully (#{client_response.response.id})")

    return redirect("clients:dashboard")
