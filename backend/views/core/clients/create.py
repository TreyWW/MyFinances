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
        "is_representative": request.POST.get("is_representative") == "on",
    }

    error = validate_client_create(client_details)

    if error:
        messages.error(request, error)
        return redirect("clients create")

    client = create_client_instance(request.user, client_details)

    if not client:
        messages.error(request, "Failed to create client - an unknown error occurred")
    else:
        messages.success(request, f"Client created successfully (#{client.id})")

    return redirect("clients dashboard")


def create_client_instance(user, client_details):
    organization = user.logged_in_as_team if user.logged_in_as_team else None
    try:
        client = Client.objects.create(organization=organization, **client_details)
        return client
    except Exception as e:
        print(f"Failed to create client: {e}")
        return None


def validate_client_create(client_details):
    name = client_details.get("name")
    company = client_details.get("company")
    is_representative = client_details.get("is_representative")

    if not name:
        return "Please provide at least a client name"

    if len(name) < 3:
        return "Client name must be at least 3 characters"

    if is_representative and not company:
        return "Please provide a company name if you are creating a representative"

    return None
