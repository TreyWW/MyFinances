from django.contrib import messages
from django.shortcuts import render, redirect

from backend.decorators import web_require_scopes
from backend.models import Invoice
from backend.types.htmx import HtmxHttpRequest


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard(request: HtmxHttpRequest):
    return render(request, "pages/invoices/dashboard/dashboard.html")


@web_require_scopes("invoices:read", False, False, "dashboard")
def invoices_dashboard_id(request: HtmxHttpRequest, invoice_id):
    if invoice_id == "create":
        return redirect("invoices:create")
    elif not isinstance(invoice_id, int):
        messages.error(request, "Invalid invoice ID")
        return redirect("invoices:dashboard")

    try:
        Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return redirect("invoices:dashboard")
    return render(request, "pages/invoices/dashboard/dashboard.html")
