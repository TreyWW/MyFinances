from backend.models import InvoiceRecurringSet, User, Organization
from backend.types.requests import WebRequest
from backend.utils.dataclasses import BaseServiceResponse


class GetRecurringSetServiceResponse(BaseServiceResponse[InvoiceRecurringSet]): ...


def get_invoice_set(request: WebRequest, invoice_set_id: int | str, check_permissions: bool = True, actor: User | Organization = None):
    actor = actor or request.actor
    try:
        invoice_set = InvoiceRecurringSet.objects.get(id=invoice_set_id)
    except InvoiceRecurringSet.DoesNotExist:
        return GetRecurringSetServiceResponse(error_message="Invoice Set not found", status_code=404)

    if check_permissions:
        if not invoice_set.has_access(actor):
            return GetRecurringSetServiceResponse(
                error_message="You do not have permission to view this invoice set",
                status_code=403,
            )

    return GetRecurringSetServiceResponse(True, invoice_set)
