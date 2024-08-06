from backend.models import InvoiceRecurringSet
from backend.utils.dataclasses import BaseServiceResponse


class ValidateFrequencyServiceResponse(BaseServiceResponse[None]):
    response: None = None


def validate_and_update_frequency(
    invoice_set: InvoiceRecurringSet, frequency: str, frequency_day_of_week: str, frequency_day_of_month: str, frequency_month_of_year: str
) -> ValidateFrequencyServiceResponse:
    """
    Will update invoice_set if success, (STILL NEED TO RUN .save())
    """
    if not isinstance(frequency, str):
        return ValidateFrequencyServiceResponse(error_message="Invalid frequency")

    match frequency.lower():
        # region Weekly
        case "weekly":
            if frequency_day_of_week not in [i for i in "0123456"]:
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the week")

            invoice_set.frequency = InvoiceRecurringSet.Frequencies.WEEKLY
            invoice_set.day_of_week = int(frequency_day_of_week)
        # endregion Weekly
        # region Monthly
        case "monthly":
            try:
                frequency_day_of_month = int(frequency_day_of_month)
            except ValueError:
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the month")

            if frequency_day_of_month < -1 or frequency_day_of_month > 28:
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the month")

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
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the month and month of the year")

            invoice_set.frequency = InvoiceRecurringSet.Frequencies.YEARLY
            invoice_set.day_of_month = frequency_day_of_month
            invoice_set.month_of_year = frequency_month_of_year
        # endregion Yearly
        case _:
            return ValidateFrequencyServiceResponse(error_message="Invalid frequency")
    # endregion Match Frequency
    return ValidateFrequencyServiceResponse(success=True)
