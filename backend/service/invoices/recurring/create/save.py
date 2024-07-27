from datetime import datetime

from django.contrib import messages
from django.core.exceptions import ValidationError

from backend.models import InvoiceRecurringSet, Client, QuotaUsage, Invoice
from backend.service.invoices.create.create import save_invoice_common
from backend.types.requests import WebRequest
from backend.utils.dataclasses import BaseServiceResponse


class SaveInvoiceServiceResponse(BaseServiceResponse[InvoiceRecurringSet]): ...


def save_invoice(request: WebRequest, invoice_items) -> SaveInvoiceServiceResponse:
    currency = request.user.user_profile.currency

    end_date = request.POST.get("end_date")

    try:
        if end_date:
            datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        return SaveInvoiceServiceResponse(error_message="Please enter a valid end date")
    finally:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

    invoice_set = InvoiceRecurringSet(
        end_date=end_date,
        date_issued=request.POST.get("date_issued"),
        currency=currency,
    )

    save_invoice_common(request, invoice_items, invoice_set)

    frequency = request.POST.get("frequency", "")
    frequency_day_of_week = request.POST.get("frequency_day_of_week", "")
    frequency_day_of_month = request.POST.get("frequency_day_of_month", "")
    frequency_month_of_year = request.POST.get("frequency_month_of_year", "")

    # Weekly = day_of_week
    # Monthly = day_of_month
    # Yearly = day_of_month + month_of_year

    # region Match Frequency
    match frequency.lower():
        # region Weekly
        case "weekly":
            if frequency_day_of_week not in [i for i in "0123456"]:
                return SaveInvoiceServiceResponse(error_message="Please select a valid day of the week")

            invoice_set.frequency = InvoiceRecurringSet.Frequencies.WEEKLY
            invoice_set.day_of_week = int(frequency_day_of_week)
        # endregion Weekly
        # region Monthly
        case "monthly":
            try:
                frequency_day_of_month = int(frequency_day_of_month)
            except ValueError:
                return SaveInvoiceServiceResponse(error_message="Please select a valid day of the month")

            if frequency_day_of_month < -1 or frequency_day_of_month > 28:
                return SaveInvoiceServiceResponse(error_message="Please select a valid day of the month")

            invoice_set.frequency = InvoiceRecurringSet.Frequencies.MONTHLY
            invoice_set.day_of_month = frequency_day_of_month
        # endregion Monthly
        # region Yearly
        case "yearly":
            try:
                frequency_day_of_month = int(frequency_day_of_month)
                frequency_month_of_year = int(frequency_month_of_year)

                if frequency_day_of_month < -1 or frequency_day_of_month > 28:
                    raise ValueError

                if frequency_month_of_year < 1 or frequency_month_of_year > 12:
                    raise ValueError
            except ValueError:
                return SaveInvoiceServiceResponse(error_message="Please select a valid day of the month and month of the year")

            invoice_set.frequency = InvoiceRecurringSet.Frequencies.YEARLY
            invoice_set.day_of_month = frequency_day_of_month
            invoice_set.month_of_year = frequency_month_of_year
        # endregion Yearly
        case _:
            return SaveInvoiceServiceResponse(error_message="Invalid frequency")
    # endregion Match Frequency

    try:
        invoice_set.full_clean()
    except ValidationError as validation_errors:
        for field, error in validation_errors.error_dict.items():
            for e in error:
                messages.error(request, f"{field}: {e.messages[0]}")
        return SaveInvoiceServiceResponse(error_message="There's at least one invalid input; please check the above error messages")

    invoice_set.save()
    invoice_set.items.set(invoice_items)

    QuotaUsage.create_str(request.user, "invoices-count", invoice_set.id)

    return SaveInvoiceServiceResponse(True, invoice_set)
