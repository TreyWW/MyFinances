from django.contrib import messages
from django.shortcuts import render, redirect
from login_required import login_not_required

from backend.models import Invoice, UserSettings, InvoiceURL


def preview(request, id):
    context = {"type": "preview"}

    try:
        invoice = Invoice.objects.get(user=request.user, id=id)
    except Invoice.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("invoices dashboard")

    try:
        currency_symbol = (
            UserSettings.objects.get(user=request.user).get_currency_symbol or "$"
        )
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    return render(
        request,
        "core/pages/invoices/view/invoice.html",
        context,
    )


@login_not_required
def view(request, uuid):
    context = {"type": "view"}

    try:
        url = InvoiceURL.objects.get(uuid=uuid)
        invoice = url.invoice
        if not invoice:
            raise InvoiceURL.DoesNotExist
    except InvoiceURL.DoesNotExist:
        messages.error(request, "Invoice not found")
        return redirect("index")

    try:
        currency_symbol = (
            UserSettings.objects.get(user=request.user).get_currency_symbol or "$"
        )
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    return render(
        request,
        "core/pages/invoices/view/invoice.html",
        context,
    )
