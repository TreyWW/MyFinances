from dataclasses import dataclass
from typing import Optional

from PIL import Image
from django.http import QueryDict

from backend.models import DefaultValues, Client
from backend.types.requests import WebRequest
from backend.utils.dataclasses import BaseServiceResponse


class ClientDefaultsServiceResponse(BaseServiceResponse[DefaultValues]): ...


def change_client_defaults(request: WebRequest, defaults: DefaultValues) -> ClientDefaultsServiceResponse:

    # put = QueryDict(request.body)
    invoice_due_date_option = request.POST.get("invoice_due_date_option","")
    invoice_due_date_value = request.POST.get("invoice_due_date_value","")

    invoice_date_option = request.POST.get("invoice_date_option","")
    invoice_date_value = request.POST.get("invoice_date_value","")

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
    if request.FILES.get("logo") is not None:
        # an image was uploaded
        logo_ok = validate_invoice_default_logo(request.FILES.get("logo"))
        if logo_ok == "ok":
            defaults.default_invoice_logo = request.FILES.get("logo")
        else:
            return ClientDefaultsServiceResponse(error_message=logo_ok)

    defaults.save()
    return ClientDefaultsServiceResponse(True)


def validate_invoice_default_logo(default_invoice_logo) -> str:
    if not default_invoice_logo:
        return "Invalid image file"
    try:
        max_file_size = 10 * 1024 * 1024

        if default_invoice_logo.size is None:
            return "Invalid image file"

        if default_invoice_logo.size > max_file_size:
            return "File size should be less or equal to 10MB"

        img = Image.open(default_invoice_logo)
        img.verify()

        if img.format is None or img.format.lower() not in ["jpeg", "png", "jpg"]:
            return "Unsupported image format. We support only JPEG, JPG, PNG, if you have a good extension, your file just got renamed."
    except (FileNotFoundError, Image.UnidentifiedImageError):
        return "Invalid or unsupported image file"
    return "ok"


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
