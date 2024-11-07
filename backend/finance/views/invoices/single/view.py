from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from login_required import login_not_required

from backend.decorators import web_require_scopes
from backend.finance.models import Invoice, InvoiceURL
from backend.core.types.htmx import HtmxHttpRequest
from backend.finance.models import InvoiceHistory
from datetime import datetime
from django.db import transaction


@web_require_scopes("invoices:read", False, False, "dashboard")
def preview(request: HtmxHttpRequest, invoice_id: str) -> HttpResponse:
    invoice: Invoice | None = Invoice.objects.filter(id=invoice_id).prefetch_related("items").first()

    if not invoice:
        messages.error(request, "Invoice not found")
        return redirect("finance:invoices:single:dashboard")

    if not invoice.has_access(request.user):
        messages.error(request, "You don't have access to this invoice")
        return redirect("finance:invoices:single:dashboard")

    # if response := generate_pdf(invoice, "inline"):
    #     return response
    return render(
        request,
        "pages/invoices/single/view/invoice_page.html",
        {"invoice": invoice},
    )


@login_not_required
def view_invoice_with_uuid_endpoint(request, uuid):
    context = {"type": "view"}

    try:
        url = InvoiceURL.objects.select_related("invoice").prefetch_related("invoice", "invoice__items").get(uuid=uuid)
        invoice = url.invoice
        if not invoice:
            raise InvoiceURL.DoesNotExist
    except InvoiceURL.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("index")

    currency_symbol = invoice.get_currency_symbol()

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    return render(
        request,
        "pages/invoices/single/view/invoice_page.html",
        context,
    )


@web_require_scopes("invoices:edit", False, False, "dashboard")
def restore_invoice_version(request, invoice_id, version):
    if request.method == "POST":
        invoice = get_object_or_404(Invoice, id=invoice_id)
        # check if user access to invoice
        if not invoice.has_access(request.user):
            messages.error(request, "You don't have permission to restore this invoice.")
            return redirect("finance:invoices:single:overview", invoice_id=invoice.id)

        InvoiceHistory.restore_version(invoice, version, save=True)
        messages.success(request, f"The invoice has been updated to version {version}.")
    return redirect("finance:invoices:single:overview", invoice_id=invoice.id)


@web_require_scopes("invoices:read", False, False, "dashboard")
def preview_invoice_version(request, invoice_id, version):
    invoice = get_object_or_404(Invoice, id=invoice_id)

    if not invoice.has_access(request.user):
        messages.error(request, "You don't have access to this invoice")
        return redirect("finance:invoices:single:dashboard")

    # save previous items
    original_items = list(invoice.items.all())

    try:
        with transaction.atomic():
            history_entry = InvoiceHistory.objects.get(invoice=invoice, version=version)

            # temporary restore items from invoice
            InvoiceHistory.restore_version(invoice, version, save=False)
            context = {
                "invoice": invoice,
                "is_history_preview": True,
                "history_entry": history_entry,
            }

            # render with temporary items
            response = render(request, "pages/invoices/single/view/invoice_page.html", context)

            # reload previous state
            invoice.items.set(original_items)

            return response

    except Exception as e:
        invoice.items.set(original_items)
        raise e
