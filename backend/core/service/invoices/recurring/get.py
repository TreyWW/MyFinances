from backend.finance.models import InvoiceRecurringProfile
from backend.core.types.requests import WebRequest
from backend.core.utils.dataclasses import BaseServiceResponse


class GetRecurringSetServiceResponse(BaseServiceResponse[InvoiceRecurringProfile]): ...


def get_invoice_profile(request: WebRequest, invoice_profile_id: int | str, check_permissions: bool = True):
    try:
        invoice_profile = InvoiceRecurringProfile.objects.get(id=invoice_profile_id, active=True)
    except InvoiceRecurringProfile.DoesNotExist:
        return GetRecurringSetServiceResponse(error_message="invoice recurring profile not found", status_code=404)

    if check_permissions:
        if not invoice_profile.has_access(request.user):
            return GetRecurringSetServiceResponse(
                error_message="You do not have permission to view this invoice recurring profile",
                status_code=403,
            )

    return GetRecurringSetServiceResponse(True, invoice_profile)
