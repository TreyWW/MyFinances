from django.contrib import messages
from django.shortcuts import render, redirect
from login_required import login_not_required

from backend.models import Invoice, UserSettings, InvoiceURL


def preview(request, invoice_id):
    context = {"type": "preview"}

    invoice = Invoice.objects.filter(id=invoice_id).prefetch_related("items").first()

    if not invoice:
        messages.error(request, "Invoice not found")
        return redirect("invoices dashboard")

    if request.user.logged_in_as_team and invoice.organization != request.user.logged_in_as_team:
        messages.error(request, "You don't have access to this invoice")
        return redirect("invoices dashboard")
    elif invoice.user != request.user:
        messages.error(request, "You don't have access to this invoice")
        return redirect("invoices dashboard")

    try:
        currency_symbol = request.user.user_profile.get_currency_symbol
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    return render(
        request,
        "pages/invoices/view/invoice.html",
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

    try:
        currency_symbol = request.user.user_profile.get_currency_symbol
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    return render(
        request,
        "pages/invoices/view/invoice.html",
        context,
    )
