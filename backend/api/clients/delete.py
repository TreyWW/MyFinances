from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods

from backend.models import Client
from backend.types.htmx import HtmxHttpRequest


@require_http_methods(["DELETE"])
@login_required
def client_delete(request: HtmxHttpRequest, id: int):
    try:
        client = Client.objects.get(id=id)
    except Client.DoesNotExist:
        messages.error(request, "Client not found")
        return render(request, "pages/clients/dashboard/_table.html", {"delete": True})

    if not client:
        messages.error(request, "Client not found")
        return render(request, "pages/clients/dashboard/_table.html", {"delete": True})

    if not request.user.is_authenticated:
        messages.error(request, "You do not have permission to delete this invoice")
        return render(request, "pages/clients/dashboard/_table.html", {"delete": True})

    client.delete()
    messages.success(request, f'Client "{client.name}" deleted successfully')

    if request.user.logged_in_as_team:
        return render(
            request,
            "pages/clients/dashboard/_table.html",
            {"clients": Client.objects.filter(organization=request.user.logged_in_as_team).order_by("-name"), "delete": True},
        )
    else:
        return render(
            request,
            "pages/clients/dashboard/_table.html",
            {"clients": Client.objects.filter(user=request.user).order_by("-name"), "delete": True},
        )
