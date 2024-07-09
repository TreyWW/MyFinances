from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.service.clients.get import fetch_clients
from backend.types.htmx import HtmxHttpRequest


@require_http_methods(["GET"])
@web_require_scopes("clients:read", True, True)
def fetch_all_clients(request: HtmxHttpRequest):
    if not request.htmx:
        return redirect("clients:dashboard")

    search_text = request.GET.get("search")

    clients = fetch_clients(request, search_text=search_text, team=request.user.logged_in_as_team)

    return render(request, "pages/clients/dashboard/_table.html", {"clients": clients})


@require_http_methods(["GET"])
@web_require_scopes("clients:read", True, True)
def fetch_clients_dropdown(request: HtmxHttpRequest):
    if not request.htmx:
        return redirect("clients:dashboard")

    selected_client = request.GET.get("existing_client_id") or None
    clients = fetch_clients(request)

    return render(
        request,
        "pages/invoices/create/_view_clients_dropdown.html",
        {"clients": clients, "selected_client": selected_client},
    )
