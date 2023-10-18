from django.contrib import messages
from django.shortcuts import render, redirect

from backend.models import Invoice, UserSettings


def preview(request, id):
    if not id or not id.isdigit():
        messages.error(request, "Invalid invoice id")
        return redirect("invoices dashboard")
    invoice = Invoice.objects.filter(user=request.user, id=id).first()
    if not invoice:
        messages.error(request, "Invoice not found")
        return redirect("invoices dashboard")
    users_currency = UserSettings.objects.filter(user=request.user).first()
    currency_symbol = "$"
    if users_currency:
        currency = users_currency.currency
        currency_symbol = UserSettings.CURRENCIES.get(currency, {}).get("symbol", "$")

    return render(
        request,
        "core/pages/invoices/view/invoice.html",
        {"invoice": invoice, "currency_symbol": currency_symbol},
    )
