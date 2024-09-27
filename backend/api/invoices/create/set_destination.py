from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.models import Client
from backend.types.htmx import HtmxHttpRequest

to_get = ["name", "address", "city", "country", "company", "is_representative", "email"]


@require_http_methods(["POST"])
def set_destination_to(request: HtmxHttpRequest):
    context: dict = {"swapping": True}

    context.update({f"to_{key}": request.POST.get(key, "") for key in to_get})

    use_existing = True if request.POST.get("use_existing") == "true" else False
    selected_client = request.POST.get("selected_client") if use_existing else None

    if selected_client:
        try:
            client = Client.objects.get(user=request.user, id=selected_client)
            context["existing_client"] = client
        except Client.DoesNotExist:
            messages.error(request, "Client not found")

    return render(request, "pages/invoices/create/destinations/_to_destination.html", context)


@require_http_methods(["POST"])
def set_destination_from(request: HtmxHttpRequest):
    context: dict = {"swapping": True}

    context.update({f"from_{key}": request.POST.get(key, "") for key in to_get})

    return render(request, "pages/invoices/create/destinations/_from_destination.html", context)
