from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
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
        return JsonResponse({"message": "Client not found"}, status=404)

    if not client:
        return JsonResponse({"message": "Client not found"}, status=404)

    if not request.user.is_authenticated:
        return JsonResponse({"message": "You do not have permission to delete this invoice"}, status=404)

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
