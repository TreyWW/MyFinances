from django.contrib import messages
from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods, require_POST

from backend.decorators import not_customer
from backend.models import Client, AuditLog


# @require_POST
@require_http_methods(["DELETE"])
@not_customer
def delete_client(request: HttpRequest, client_id: int):
    if not request.htmx:
        return redirect("clients dashboard")

    if request.user.logged_in_as_team:
        clients = Client.objects.filter(organization=request.user.logged_in_as_team, active=True)
        audit_log = AuditLog(organization=request.user.logged_in_as_team)
    else:
        clients = Client.objects.filter(user=request.user, active=True)
        audit_log = AuditLog(user=request.user)

    client = clients.filter(id=client_id)

    if not client:
        messages.error(request, "Client not found")
        return render(request, "base/toasts.html")  # htmx will handle the toast

    audit_log.action = f"Deleted client #{client_id}"
    audit_log.save()
    client.delete()

    messages.success(request, f"Client #{client_id} was successfully deleted.")

    return render(request, "base/toasts.html")  # htmx will handle the toast


@require_http_methods(["GET"])
@not_customer
def fetch_clients_dropdown(request: HttpRequest):
    if not request.htmx:
        return redirect("clients dashboard")

    selected_client = request.GET.get("existing_client_id") or None
    clients = Client.objects.filter(user=request.user, active=True)

    return render(
        request,
        "pages/invoices/create/_view_clients_dropdown.html",
        {"clients": clients, "selected_client": selected_client},
    )
