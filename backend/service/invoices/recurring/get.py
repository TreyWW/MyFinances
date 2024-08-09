from backend.models import InvoiceRecurringProfile, User, Organization
from backend.types.requests import WebRequest
from backend.utils.dataclasses import BaseServiceResponse


class GetRecurringSetServiceResponse(BaseServiceResponse[InvoiceRecurringProfile]): ...


def get_invoice_set(request: WebRequest, invoice_set_id: int | str, check_permissions: bool = True):
    try:
        invoice_set = InvoiceRecurringProfile.objects.get(id=invoice_set_id, active=True)
    except InvoiceRecurringProfile.DoesNotExist:
        return GetRecurringSetServiceResponse(error_message="Invoice Set not found", status_code=404)

    if check_permissions:
        if not invoice_set.has_access(request.user):
            return GetRecurringSetServiceResponse(
                error_message="You do not have permission to view this invoice set",
                status_code=403,
            )

    return GetRecurringSetServiceResponse(True, invoice_set)
