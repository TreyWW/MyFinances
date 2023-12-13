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
    client_company = request.POST.get("company_name")
    is_representiative = request.POST.get("is_representative")

    error = validate_client_create(client_name, client_company, is_representiative)

    if error:
        messages.error(request, error)
        return redirect("clients create")

    client = Client.objects.create(
        user=request.user,
        name=client_name,
        email=client_email,
        address=client_address,
        phone_number=client_phone,
    )

    if is_representiative:
        client.is_representative = True
        client.company = client_company

    if client:
        messages.success(request, f"Client created successfully (#{client.id})")
    else:
        messages.error(request, "Failed to create client - an unknown error occurred")
    return redirect("clients dashboard")


def validate_client_create(client_name, client_company, is_representiative):
    if not client_name:
        return "Please provide at least a client name"

    if len(client_name) < 3:
        return "Client name must be at least 3 characters"

    if is_representiative and not client_company:
        return "Please provide a company name if you are creating a representative"

    return None
