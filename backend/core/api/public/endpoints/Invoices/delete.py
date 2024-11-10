from django.http import QueryDict
from rest_framework import status
from rest_framework.decorators import api_view

from backend.core.api.public.decorators import require_scopes
from backend.core.api.public.types import APIRequest
from backend.core.api.public.helpers.response import APIResponse

from backend.models import Invoice, QuotaLimit


@api_view(["DELETE"])
@require_scopes(["invoices:write"])
def delete_invoice_endpoint(request: APIRequest):
    delete_items = QueryDict(request.body)

    try:
        invoice = Invoice.objects.get(id=delete_items.get("invoice", ""))
    except Invoice.DoesNotExist:
        return APIResponse(False, {"error": "Invoice Not Found"}, status=status.HTTP_404_NOT_FOUND)

    if not invoice.has_access(request.user):
        return APIResponse(False, {"error": "You do not have permission to delete this invoice"}, status=status.HTTP_403_FORBIDDEN)

    QuotaLimit.delete_quota_usage("invoices-count", request.user, invoice.id, invoice.date_created)

    invoice.delete()

    return APIResponse(True, {"message": "Invoice successfully deleted"}, status=status.HTTP_200_OK)
