from datetime import datetime
from typing import Literal

from rest_framework import status
from rest_framework.decorators import api_view

from backend.core.api.public.decorators import require_scopes
from backend.core.api.public.types import APIRequest
from backend.core.api.public.helpers.response import APIResponse
from backend.finance.models import Invoice


@api_view(["POST"])
@require_scopes(["invoices:write"])
def edit_invoice_endpoint(request: APIRequest):
    invoice_id = request.data.get("invoice_id", "")
    if not invoice_id:
        return APIResponse(False, {"error": "Invoice ID is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return APIResponse(False, {"error": "Invoice Not Found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.logged_in_as_team and request.user.logged_in_as_team != invoice.organization:
        return APIResponse(
            False,
            {"error": "You do not have permission to edit this invoice"},
            status=status.HTTP_403_FORBIDDEN,
        )
    elif request.user != invoice.user:
        return APIResponse(
            False,
            {"error": "You do not have permission to edit this invoice"},
            status=status.HTTP_403_FORBIDDEN,
        )

    attributes_to_updates = {
        "date_due": request.POST.get("date_due"),
        "date_issued": request.POST.get("date_issued"),
        "client_name": request.POST.get("to_name"),
        "client_company": request.POST.get("to_company"),
        "client_email": request.POST.get("to_email"),
        "client_address": request.POST.get("to_address"),
        "client_city": request.POST.get("to_city"),
        "client_county": request.POST.get("to_county"),
        "client_country": request.POST.get("to_country"),
        "self_name": request.POST.get("from_name"),
        "self_company": request.POST.get("from_company"),
        "self_address": request.POST.get("from_address"),
        "self_city": request.POST.get("from_city"),
        "self_county": request.POST.get("from_county"),
        "self_country": request.POST.get("from_country"),
        "notes": request.POST.get("notes"),
        "vat_number": request.POST.get("vat_number"),
        "reference": request.POST.get("reference"),
        "sort_code": request.POST.get("sort_code"),
        "account_number": request.POST.get("account_number"),
        "account_holder_name": request.POST.get("account_holder_name"),
    }

    for column_name, new_value in attributes_to_updates.items():
        if new_value is not None:
            if column_name == "date_due":
                try:
                    new_value = datetime.strptime(new_value, "%Y-%m-%d").date()  # type: ignore[assignment]
                except ValueError:
                    return APIResponse(False, {"error": "Invalid date format for date_due"}, status=status.HTTP_400_BAD_REQUEST)
            setattr(invoice, column_name, new_value)

    invoice.save()

    return APIResponse(True, {"message": "Invoice successfully edited"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def change_status_endpoint(request, invoice_id: int, invoice_status: str):
    new_status = invoice_status.lower() if invoice_status else ""

    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return APIResponse(False, {"error": "Invoice Not Found"}, status=status.HTTP_404_NOT_FOUND)

    if request.user.logged_in_as_team and request.user.logged_in_as_team != invoice.organization or request.user != invoice.user:
        return APIResponse(False, {"error": "You do not have permission to edit this invoice"}, status=status.HTTP_403_FORBIDDEN)

    if invoice.status == new_status:
        return APIResponse(False, {"error": f"Invoice status is already {new_status}"}, status=status.HTTP_400_BAD_REQUEST)

    if not invoice.set_status(new_status, save=True):
        return APIResponse(False, {"error": "Invalid status. Please choose from: pending, paid, draft"}, status=status.HTTP_400_BAD_REQUEST)

    return APIResponse(True, {"message": f"Invoice status been changed to <strong>{new_status}</strong>"}, status=status.HTTP_200_OK)


@api_view(["POST"])
def edit_discount_endpoint(request, invoice_id: str):
    discount_type = "percentage" if request.data.get("discount_type") == "on" else "amount"
    discount_amount_str: str = request.data.get("discount_amount", "")
    percentage_amount_str: str = request.data.get("percentage_amount", "")

    try:
        invoice: Invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return APIResponse(False, {"error": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

    if not invoice.has_access(request.user):
        return APIResponse(False, {"error": "You don't have permission to make changes to this invoice."}, status=status.HTTP_403_FORBIDDEN)

    if discount_type == "percentage":
        try:
            percentage_amount = int(percentage_amount_str)
            if percentage_amount < 0 or percentage_amount > 100:
                raise ValueError
        except ValueError:
            return APIResponse(
                False, {"error": "Please enter a valid percentage amount (between 0 and 100)"}, status=status.HTTP_400_BAD_REQUEST
            )
        invoice.discount_percentage = percentage_amount
    else:
        try:
            discount_amount = int(discount_amount_str)
            if discount_amount < 0:
                raise ValueError
        except ValueError:
            return APIResponse(False, {"error": "Please enter a valid discount amount"}, status=status.HTTP_400_BAD_REQUEST)
        invoice.discount_amount = discount_amount

    invoice.save()

    return APIResponse(True, {"message": "Discount was applied successfully"}, status=status.HTTP_200_OK)
