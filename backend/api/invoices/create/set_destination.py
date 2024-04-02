from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models.client import Client

to_get = ["name", "address", "city", "country", "company", "is_representative"]


@require_http_methods(["POST"])
def set_destination_to(request: HttpRequest):
    context = {"swapping": True}

    context.update({key: request.POST.get(key) for key in to_get})

    use_existing = True if request.POST.get("use_existing") == "true" else False
    selected_client = request.POST.get("selected_client") if use_existing else None

    if selected_client:
        try:
            client = Client.objects.get(user=request.user, id=selected_client)
            context["existing_client"] = client
        except Client.DoesNotExist:
            messages.error("Client not found")

    return render(request, "pages/invoices/create/_to_destination.html", context)


@require_http_methods(["POST"])
def set_destination_from(request: HttpRequest):
    context = {"swapping": True}

    context.update({key: request.POST.get(key) for key in to_get})

    return render(request, "pages/invoices/create/_from_destination.html", context)
