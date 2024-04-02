from dataclasses import dataclass
from typing import Literal, TypedDict

from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.models import UserSettings
from backend.models_db.invoice import Invoice


class PreviewContext(TypedDict):
    type: Literal["preview"]
    invoice: Invoice
    currency_symbol: str


@dataclass(frozen=True)
class SuccessResponse:
    context: PreviewContext
    success: Literal[True] = True


@dataclass(frozen=True)
class ErrorResponse:
    message: str
    success: Literal[False] = False


@require_http_methods(["GET"])
def tab_preview_invoice(request: HttpRequest, invoice_id):
    # Redirect if not an HTMX request
    if not request.htmx:
        return redirect("invoices dashboard")  # Maybe should be 404?

    prev_invoice = preview_invoice(request, invoice_id)

    if prev_invoice.success:
        return render(request, "pages/invoices/view/invoice.html", prev_invoice.context)

    messages.error(request, prev_invoice.message)

    return render(request, "base/toasts.html")


def preview_invoice(request: HttpRequest, invoice_id) -> SuccessResponse | ErrorResponse:
    context = {"type": "preview"}

    try:
        invoice = Invoice.objects.prefetch_related("items").get(id=invoice_id)

    except Invoice.DoesNotExist:
        return ErrorResponse("Invoice not found")

    if request.user.logged_in_as_team:
        if invoice.organization != request.user.logged_in_as_team:
            return ErrorResponse("You don't have access to this invoice")
    else:
        if invoice.user != request.user:
            return ErrorResponse("You don't have access to this invoice")
    try:
        currency_symbol = request.user.user_profile.get_currency_symbol()
    except UserSettings.DoesNotExist:
        currency_symbol = "$"

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    context_object = PreviewContext(
        type="preview",
        invoice=invoice,
        currency_symbol=currency_symbol,
    )

    return SuccessResponse(context=context_object)
