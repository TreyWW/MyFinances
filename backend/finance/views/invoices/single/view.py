from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import render
from django.http import HttpResponse

from login_required import login_not_required

from backend.decorators import web_require_scopes
from backend.finance.models import Invoice, InvoiceURL
from backend.core.types.htmx import HtmxHttpRequest


@web_require_scopes("invoices:read", False, False, "dashboard")
def preview(request: HtmxHttpRequest, invoice_id: str) -> HttpResponse:
    invoice: Invoice | None = Invoice.objects.filter(id=invoice_id).prefetch_related("items").first()
    iframed = bool(request.GET.get("iframe"))
    show_refresh_btn = bool(request.GET.get("show_refresh"))

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
        {"invoice": invoice, "iframed": iframed, "show_refresh_btn": show_refresh_btn},
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
