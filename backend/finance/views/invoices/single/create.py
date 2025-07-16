from datetime import datetime

from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from backend.decorators import web_require_scopes, has_entitlements
from backend.core.service.invoices.single.create.create import create_invoice_items, save_invoice
from backend.core.service.invoices.single.create.get_page import get_invoice_context
from backend.core.types.requests import WebRequest
from backend.finance.views.invoices.handler import invoices_core_handler
from backend.finance.models import Invoice
from backend.finance.views.invoices.single.edit import invoice_get_existing_data


@require_http_methods(["GET", "POST"])
def create_single_invoice_endpoint_handler(request: WebRequest):
    if request.method == "POST":
        return create_invoice_post_endpoint(request)
    return create_invoice_page_endpoint(request)


@require_http_methods(["GET"])
@has_entitlements("invoices")
@web_require_scopes("invoices:read", False, False, "finance:invoices:single:dashboard")
def create_invoice_page_endpoint(request: WebRequest):
    """
    Renders the create invoice  page (for single invoice).
    If `clone_from` is provided and there is access to a referenced invoice:
            - It will load existing invoice data using `invoice_get_existing_data`.
            - Sets the `reference` to a "-COPY" variant and updates issue dates to today.
            - Uses prefill key to add the prefilled data
    If the invoice is not found, add error message "Invoice to clone not found"

    Returns:
        HttpResponse: Rendered invoice creation page (`create_single.html`) with context data.
    """
    context = get_invoice_context(request)

    clone_id = request.GET.get("clone_from")
    if clone_id:
        try:
            invoice = Invoice.objects.get(id=clone_id)

            if invoice.has_access(request.user):
                cloned_data = invoice_get_existing_data(invoice)

                cloned_data["reference"] = f"{cloned_data['reference'] or ''}-COPY"
                cloned_data["from_date_issued"] = datetime.today().date()
                cloned_data["issue_date"] = datetime.today().date()

                context.update({"prefill": cloned_data})
                context.update({"rows": cloned_data.get("rows", [])})

        except Invoice.DoesNotExist:
            messages.error(request, "Invoice to clone not found")

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
