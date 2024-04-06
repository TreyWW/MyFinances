from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import redirect
from django.shortcuts import render
from login_required import login_not_required

from backend.models import Invoice
from backend.models import InvoiceURL
from backend.models import UserSettings


def preview(request, invoice_id):
    context = {"type": "preview"}

    invoice = Invoice.objects.filter(id=invoice_id).prefetch_related("items").first()

    if not invoice:
        messages.error(request, "Invoice not found")
        return redirect("invoices:dashboard")

    if request.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team:
        messages.error(request, "You don't have access to this invoice")
        return redirect("invoices:dashboard")
    elif invoice.user != request.user:
        messages.error(request, "You don't have access to this invoice")
        return redirect("invoices:dashboard")

    try:
        currency_symbol = invoice.get_currency_symbol()
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    return render(
        request,
        "pages/invoices/view/invoice_page.html",
        context,
    )


@login_not_required
def view(request, uuid):
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
        "pages/invoices/view/invoice_page.html",
        context,
    )
