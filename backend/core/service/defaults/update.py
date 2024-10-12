from PIL import Image

from backend.models import DefaultValues
from backend.core.types.requests import WebRequest
from backend.core.utils.dataclasses import BaseServiceResponse


class ClientDefaultsServiceResponse(BaseServiceResponse[DefaultValues]): ...


def change_client_defaults(request: WebRequest, defaults: DefaultValues) -> ClientDefaultsServiceResponse:

    # put = QueryDict(request.body)
    invoice_due_date_option = request.POST.get("invoice_due_date_option", "")
    invoice_due_date_value = request.POST.get("invoice_due_date_value", "")

    invoice_date_option = request.POST.get("invoice_date_option", "")
    invoice_date_value = request.POST.get("invoice_date_value", "")

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

    DETAIL_INPUTS = {
        "name": {"max_len": 100},
        "email": {"max_len": 100},
        "company": {"max_len": 100},
        "address": {"max_len": 100},
        "city": {"max_len": 100},
        "county": {"max_len": 100},
        "country": {"max_len": 100},
    }

    for detail, value_dict in DETAIL_INPUTS.items():
        input_post = request.POST.get(f"invoice_from_{detail}", "")

        if len(input_post) > value_dict["max_len"]:
            return ClientDefaultsServiceResponse(
                error_message=f"Details - From {detail} is too long, max length is {value_dict['max_len']}"
            )

        setattr(defaults, f"invoice_from_{detail}", input_post)

    PAYMENT_INPUTS = {
        "account_number": {"max_len": 100},
        "sort_code": {"max_len": 100},
        "account_holder_name": {"max_len": 100},
    }

    for detail, value_dict in PAYMENT_INPUTS.items():
        input_post = request.POST.get(f"invoice_{detail}", "")

        if len(input_post) > value_dict["max_len"]:
            return ClientDefaultsServiceResponse(error_message=f"Payment - {detail} is too long, max length is {value_dict['max_len']}")

        setattr(defaults, f"invoice_{detail}", input_post)

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
