from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes, has_entitlements
from backend.core.service.invoices.single.create.create import create_invoice_items, save_invoice
from backend.core.service.invoices.single.create.get_page import get_invoice_context
from backend.core.types.requests import WebRequest
from backend.finance.views.invoices.handler import invoices_core_handler


@require_http_methods(["GET", "POST"])
def create_single_invoice_endpoint_handler(request: WebRequest):
    if request.method == "POST":
        return create_invoice_post_endpoint(request)
    return create_invoice_page_endpoint(request)


@require_http_methods(["GET"])
@has_entitlements("invoices")
@web_require_scopes("invoices:read", False, False, "finance:invoices:single:dashboard")
def create_invoice_page_endpoint(request: WebRequest):
    context = get_invoice_context(request)
    return invoices_core_handler(request, "pages/invoices/create/create_single.html", context)


@require_http_methods(["POST"])
@has_entitlements("invoices")
@web_require_scopes("invoices:write", False, False, "finance:invoices:single:dashboard")
def create_invoice_post_endpoint(request: WebRequest):
    invoice_items = create_invoice_items(request)
    invoice = save_invoice(request, invoice_items)
    if not invoice:
        return invoices_core_handler(request, "pages/invoices/create/create_single.html")
    return redirect("finance:invoices:single:dashboard")
