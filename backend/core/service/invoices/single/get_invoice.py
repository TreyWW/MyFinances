from backend.finance.models import Invoice, Organization, User
from backend.core.utils.dataclasses import BaseServiceResponse


class GetInvoiceServiceResponse(BaseServiceResponse[Invoice]): ...


def get_invoice_by_actor(actor: User | Organization, id: str | int, prefetch_related: list[str] | None = None) -> GetInvoiceServiceResponse:
    prefetch_related_args: list[str] = prefetch_related or []
    try:
        invoice: Invoice = Invoice.filter_by_owner(actor).prefetch_related(*prefetch_related_args).get(id=id)
        return GetInvoiceServiceResponse(True, response=invoice)
    except Invoice.DoesNotExist:
        return GetInvoiceServiceResponse(False, error_message="Invoice not found")
