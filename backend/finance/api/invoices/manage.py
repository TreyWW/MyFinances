from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from typing import TypedDict

from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.finance.models import Invoice
from backend.core.types.htmx import HtmxHttpRequest


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
@web_require_scopes("invoices:read", True, True)
def preview_invoice(request: HtmxHttpRequest, invoice_id) -> SuccessResponse | ErrorResponse:
    context: dict[str, str | Invoice] = {"type": "preview"}

    try:
        invoice = Invoice.objects.prefetch_related("items").get(id=invoice_id)

    except Invoice.DoesNotExist:
        return ErrorResponse("Invoice not found")

    if not invoice.has_access(request.user):
        return ErrorResponse("You don't have access to this invoice")

    currency_symbol = invoice.get_currency_symbol()

    context.update({"invoice": invoice, "currency_symbol": currency_symbol})

    context_object = PreviewContext(
        type="preview",
        invoice=invoice,
        currency_symbol=currency_symbol,
    )

    return SuccessResponse(context=context_object)
