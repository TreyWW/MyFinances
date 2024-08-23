from dataclasses import dataclass
from typing import Optional

from django.http import QueryDict

from backend.models import DefaultValues, Client
from backend.types.requests import WebRequest
from backend.utils.dataclasses import BaseServiceResponse


class ClientDefaultsServiceResponse(BaseServiceResponse[DefaultValues]): ...


def change_client_defaults(request: WebRequest, defaults: DefaultValues) -> ClientDefaultsServiceResponse:

    # put = QueryDict(request.body)
    invoice_due_date_option = request.POST.get("invoice_due_date_option")
    invoice_due_date_value = request.POST.get("invoice_due_date_value")

    invoice_date_option = request.POST.get("invoice_date_option")
    invoice_date_value = request.POST.get("invoice_date_value")

    due_date_error = validate_invoice_due_date(invoice_due_date_option, invoice_due_date_value)

    if due_date_error.failed:
        return ClientDefaultsServiceResponse(error_message=due_date_error.error)

    invoice_date_error = validate_invoice_date(invoice_date_option, invoice_date_value)

    if invoice_date_error.failed:
        return ClientDefaultsServiceResponse(error_message=invoice_date_error.error)

    defaults.invoice_due_date_type = invoice_due_date_option
    defaults.invoice_due_date_value = invoice_due_date_value

    defaults.invoice_date_type = invoice_date_option
    defaults.invoice_date_value = invoice_date_value
    defaults.default_invoice_logo = request.FILES.get("logo")
    defaults.save()

    return ClientDefaultsServiceResponse(True)


def validate_invoice_default_logo(default_invoice_logo) -> bool:
    # If a future need to control invoice logo size and dimensions before assignment arise
    pass


def validate_invoice_due_date(due_date_type, due_date_value) -> ClientDefaultsServiceResponse:
    if due_date_type not in ["days_after", "date_following", "date_current"]:
        return ClientDefaultsServiceResponse(error_message="Invalid invoice due date type")

    try:
        due_date_value = int(due_date_value)
    except ValueError:
        return ClientDefaultsServiceResponse(error_message="Invalid invoice due date value, must be a number")

    if due_date_type == "date_following" and due_date_value < 1:
        return ClientDefaultsServiceResponse(error_message="Due date value must be greater than 0")

    if due_date_type in ["date_current", "date_following"] and (due_date_value > 31 or due_date_value < 1):
        return ClientDefaultsServiceResponse(error_message="Due date value must be between 1 and 31 days")
    return ClientDefaultsServiceResponse(True)


def validate_invoice_date(date_type, date_value) -> ClientDefaultsServiceResponse:
    if date_type not in ["day_of_month", "days_after"]:
        return ClientDefaultsServiceResponse(error_message="Invalid invoice date type")

    try:
        date_value = int(date_value)
    except ValueError:
        return ClientDefaultsServiceResponse(error_message="Invalid invoice date value, must be a number")

    if date_type == "days_after" and (date_value < 1 or date_value > 90):
        return ClientDefaultsServiceResponse(error_message="Invoice date value must be between 1 and 90 days")

    if date_type == "day_of_month" and (date_value < 1 or date_value > 31):
        return ClientDefaultsServiceResponse(error_message="Invoice date value must be between 1 and 31 days")
    return ClientDefaultsServiceResponse(True)
