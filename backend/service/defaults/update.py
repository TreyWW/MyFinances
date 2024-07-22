from django.http import QueryDict

from backend.models import DefaultValues, Client
from backend.types.requests import WebRequest


def change_client_defaults(request: WebRequest, defaults: DefaultValues) -> str | None:
    put = QueryDict(request.body)

    invoice_due_date_option = put.get("invoice_due_date_option", "")
    invoice_due_date_value = put.get("invoice_due_date_value", "")

    invoice_date_option = put.get("invoice_date_option", "")
    invoice_date_value = put.get("invoice_date_value", "")

    due_date_error = validate_invoice_due_date(invoice_due_date_option, invoice_due_date_value)
    if due_date_error:
        return due_date_error

    invoice_date_error = validate_invoice_date(invoice_date_option, invoice_date_value)
    if invoice_date_error:
        return invoice_date_error

    defaults.invoice_due_date_type = invoice_due_date_option
    defaults.invoice_due_date_value = invoice_due_date_value

    defaults.invoice_date_type = invoice_date_option
    defaults.invoice_date_value = invoice_date_value

    defaults.save()

    return None


def validate_invoice_due_date(due_date_type, due_date_value) -> str | None:
    if due_date_type not in ["days_after", "date_following", "date_current"]:
        return "Invalid invoice due date type"

    try:
        due_date_value = int(due_date_value)
    except ValueError:
        return "Invalid invoice due date value, must be a number"

    if due_date_type == "date_following" and due_date_value < 1:
        return "Due date value must be greater than 0"

    if due_date_type in ["date_current", "date_following"] and (due_date_value > 31 or due_date_value < 1):
        return "Due date value must be between 1 and 31 days"
    return None


def validate_invoice_date(date_type, date_value) -> str | None:
    if date_type not in ["day_of_month", "days_after"]:
        return "Invalid invoice date type"

    try:
        date_value = int(date_value)
    except ValueError:
        return "Invalid invoice date value, must be a number"

    if date_type == "days_after" and (date_value < 1 or date_value > 90):
        return "Invoice date value must be between 1 and 90 days"

    if date_type == "day_of_month" and (date_value < 1 or date_value > 31):
        return "Invoice date value must be between 1 and 31 days"
    return None
