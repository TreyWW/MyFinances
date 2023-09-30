from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from backend.models import Client


def clients_dashboard(request: HttpRequest):
    context = {
        "modal_data": [
            {
                "id": "modal_create_client",
                "title": "Create Client",
                "action": {
                    "text": "Create",
                    "method": "post",
                    "fields": [
                        {
                            "type": "text",
                            "name": "first_name",
                            "required": True,
                            "label": "First Name",
                            "placeholder": "John",
                            "class_extra": "input-ghost-secondary",
                        },
                        {
                            "type": "text",
                            "name": "last_name",
                            "required": True,
                            "label": "Last Name",
                            "placeholder": "Smith",
                            "class_extra": "input-ghost-secondary",
                        },
                    ],
                },
            }
        ],
        "clients": Client.objects.filter(user=request.user, active=True),
    }

    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")

        if not first_name:
            messages.error(request, "First name is required")

        if not last_name:
            messages.error(request, "Last name is required")

        if not first_name or not last_name:
            return render(
                request, "core/pages/clients/dashboard/dashboard.html", context
            )

        Client.objects.create(
            first_name=request.POST.get("first_name"),
            last_name=request.POST.get("last_name"),
            user=request.user,
        )

    return render(request, "core/pages/clients/dashboard/dashboard.html", context)
