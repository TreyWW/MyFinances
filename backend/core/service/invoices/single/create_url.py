from backend.finance.models import InvoiceURL, Invoice
from backend.core.models import User
from backend.core.utils.dataclasses import BaseServiceResponse


class CreateInvoiceURLServiceResponse(BaseServiceResponse[InvoiceURL]): ...


def create_invoice_url(invoice: Invoice, user: User | None = None) -> CreateInvoiceURLServiceResponse:
    return CreateInvoiceURLServiceResponse(
        True,
        response=InvoiceURL.objects.create(
            invoice=invoice,
            created_by=user,
        ),
    )
