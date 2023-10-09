from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from backend.models import Client


def clients_dashboard(request: HttpRequest):
    context = {
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
