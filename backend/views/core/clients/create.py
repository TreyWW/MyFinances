from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render, redirect

from backend.models import Client
from backend.types.htmx import HtmxHttpRequest


def create_client(request: HtmxHttpRequest):
    if request.method == "GET":
        return render(request, "pages/clients/create/create.html")

    client_details = {
        "name": request.POST.get("client_name"),
        "email": request.POST.get("client_email"),
        "address": request.POST.get("client_address"),
        "phone_number": request.POST.get("client_phone"),
        "company": request.POST.get("company_name"),
        "is_representative": (True if request.POST.get("is_representative") == "on" else False),
    }

    error = validate_client_create(client_details)

    if error:
        messages.error(request, error)
        return redirect("clients create")

    if request.user.logged_in_as_team:
        client = Client.objects.create(
            organization=request.user.logged_in_as_team,
        )
    else:
        client = Client.objects.create(
            user=request.user,
        )

    for model_field, new_value in client_details.items():
        setattr(client, model_field, new_value)

    client.save()

    if client:
        messages.success(request, f"Client created successfully (#{client.id})")
    else:
        messages.error(request, "Failed to create client - an unknown error occurred")
    return redirect("clients dashboard")


def validate_client_create(client_details):
    if not client_details.get("name"):
        return "Please provide at least a client name"

    if len(client_details.get("name")) < 3:
        return "Client name must be at least 3 characters"

    if client_details.get("is_representative") and not client_details.get("company"):
        return "Please provide a company name if you are creating a representative"

    return None
