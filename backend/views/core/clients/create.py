from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render, redirect

from backend.models import Client


def create_client(request: HttpRequest):
    if request.method == "GET":
        return render(request, "pages/clients/create/create.html")

    client_name = request.POST.get("client_name")
    client_email = request.POST.get("client_email")
    client_address = request.POST.get("client_address")
    client_phone = request.POST.get("client_phone")

    if not client_name:
        messages.error(request, "Please provide at least a client name")
        return redirect("clients create")

    if len(client_name) < 3:
        messages.error(request, "Client name must be at least 3 characters")
        return redirect("clients create")

    client = Client.objects.create(
        user=request.user,
        name=client_name,
        email=client_email,
        address=client_address,
        phone_number=client_phone,
    )
    if client:
        messages.success(request, f"Client created successfully (#{client.id})")
    else:
        messages.error(request, "Failed to create client - an unknown error occurred")
    return redirect("clients dashboard")
