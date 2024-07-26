from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.service.invoices.create.create import create_invoice_items
from backend.service.invoices.recurring.create.get_page import get_invoice_context
from backend.service.invoices.recurring.create.save import save_invoice
from backend.types.requests import WebRequest
from backend.views.core.invoices.handler import invoices_core_handler


@require_http_methods(["GET", "POST"])
def create_recurring_invoice_endpoint_handler(request: WebRequest):
    if request.method == "POST":
        return create_invoice_post_endpoint(request)
    return create_invoice_page_endpoint(request)


@require_http_methods(["GET"])
@web_require_scopes("invoices:read", False, False, "invoices:recurring:dashboard")
def create_invoice_page_endpoint(request: WebRequest):
    context = get_invoice_context(request)
    return invoices_core_handler(request, "pages/invoices/create/create_recurring.html", context)


@require_http_methods(["POST"])
@web_require_scopes("invoices:write", False, False, "invoices:recurring:dashboard")
def create_invoice_post_endpoint(request: WebRequest):
    invoice_items = create_invoice_items(request)
    invoice = save_invoice(request, invoice_items)
    if not invoice:
        return invoices_core_handler(request, "pages/invoices/create/create_recurring.html", {"autohide": False})
    return redirect("invoices:recurring:dashboard")
