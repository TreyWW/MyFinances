from datetime import datetime, date

from django.contrib import messages
from django.core.exceptions import ValidationError

from backend.models import InvoiceRecurringProfile, QuotaUsage
from backend.core.service.invoices.common.create.create import save_invoice_common
from backend.core.service.invoices.recurring.validate.frequencies import validate_and_update_frequency
from backend.core.types.requests import WebRequest
from backend.core.utils.dataclasses import BaseServiceResponse


class SaveInvoiceServiceResponse(BaseServiceResponse[InvoiceRecurringProfile]): ...


def save_invoice(request: WebRequest, invoice_items) -> SaveInvoiceServiceResponse:
    currency = request.user.user_profile.currency

    end_date_str: str = request.POST.get("end_date", "")

    try:
        if end_date_str:
            datetime.strptime(end_date_str, "%Y-%m-%d").date()
    except ValueError:
        return SaveInvoiceServiceResponse(error_message="Please enter a valid end date")
    finally:
        end_date_obj: date | None = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str else None

    invoice_profile = InvoiceRecurringProfile(
        end_date=end_date_obj,
        date_issued=request.POST.get("date_issued"),
        currency=currency,
    )

    save_invoice_common(request, invoice_items, invoice_profile)

    frequency = request.POST.get("frequency", "")
    frequency_day_of_week = request.POST.get("frequency_day_of_week", "")
    frequency_day_of_month = request.POST.get("frequency_day_of_month", "")
    frequency_month_of_year = request.POST.get("frequency_month_of_year", "")

    # Weekly = day_of_week
    # Monthly = day_of_month
    # Yearly = day_of_month + month_of_year

    frequency_validate_response = validate_and_update_frequency(
        invoice_profile=invoice_profile,
        frequency=frequency,
        frequency_day_of_week=frequency_day_of_week,
        frequency_day_of_month=frequency_day_of_month,
        frequency_month_of_year=frequency_month_of_year,
    )

    if frequency_validate_response.failed:
        messages.error(request, frequency_validate_response.error_message)
        return SaveInvoiceServiceResponse(error_message="There's at least one invalid input; please check the above error messages")

    try:
        invoice_profile.full_clean()

        if frequency_validate_response.failed:
            raise ValidationError({"Frequency": frequency_validate_response.error})
    except ValidationError as validation_errors:
        for field, error in validation_errors.error_dict.items():
            for e in error:
                messages.error(request, f"{field}: {e.messages[0]}")
        return SaveInvoiceServiceResponse(error_message="There's at least one invalid input; please check the above error messages")

    invoice_profile.save()
    invoice_profile.items.set(invoice_items)

    QuotaUsage.create_str(request.user, "invoices-count", invoice_profile.id)

    return SaveInvoiceServiceResponse(True, invoice_profile)
