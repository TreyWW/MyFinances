from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.models import Client


@require_http_methods(["GET"])
def fetch_all_clients(request: HttpRequest):
    if not request.htmx:
        return redirect("clients dashboard")

    search_text = request.GET.get("search")

    clients = Client.objects.filter(user=request.user, active=True)

    if search_text:
        clients = clients.filter(
            Q(name__icontains=search_text)
            | Q(email__icontains=search_text)
            | Q(id__icontains=search_text)
        )

    return render(request, "pages/clients/dashboard/_table.html", {"clients": clients})
