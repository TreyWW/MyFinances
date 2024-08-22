from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import Invoice
from backend.types.requests import WebRequest
from backend.views.core.invoices.handler import invoices_core_handler


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_single_dashboard_endpoint(request: WebRequest):
    return invoices_core_handler(request, "pages/invoices/single/dashboard/dashboard.html")


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard_id(request: WebRequest, invoice_id):
    if invoice_id == "create":
        return redirect("invoices:single:create")
    elif not isinstance(invoice_id, int):
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices:single:dashboard")

    try:
        Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return redirect("invoices:single:dashboard")
    return render(request, "pages/invoices/single/dashboard/dashboard.html")
