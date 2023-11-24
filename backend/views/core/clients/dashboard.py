from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render
from django.urls import reverse_lazy
from backend.models import Client


def clients_dashboard(request: HttpRequest):
    context = {}
    if request.htmx:
        context["clients"] = Client.objects.filter(user=request.user, active=True)
        return render(request, "pages/clients/dashboard/_table.html", context)

    return render(request, "pages/clients/dashboard/dashboard.html", context)
