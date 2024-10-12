from backend.finance.models import InvoiceRecurringProfile
from backend.core.utils.dataclasses import BaseServiceResponse


class ValidateFrequencyServiceResponse(BaseServiceResponse[None]):
    response: None = None


def validate_and_update_frequency(
    invoice_profile: InvoiceRecurringProfile,
    frequency: str,
    frequency_day_of_week: str,
    frequency_day_of_month: str,
    frequency_month_of_year: str,
) -> ValidateFrequencyServiceResponse:
    """
    Will update invoice_profile if success, (STILL NEED TO RUN .save())
    """
    if not isinstance(frequency, str):
        return ValidateFrequencyServiceResponse(error_message="Invalid frequency")

    frequency_day_of_month_int: int
    frequency_day_of_week_int: int
    frequency_month_of_year_int: int

    match frequency.lower():
        # region Weekly
        case "weekly":
            if frequency_day_of_week not in [i for i in "1234567"]:
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the week")

            invoice_profile.frequency = InvoiceRecurringProfile.Frequencies.WEEKLY
            invoice_profile.day_of_week = int(frequency_day_of_week)
        # endregion Weekly
        # region Monthly
        case "monthly":
            try:
                frequency_day_of_month_int = int(frequency_day_of_month)
            except ValueError:
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the month")

            if frequency_day_of_month_int < -1 or frequency_day_of_month_int > 28:
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the month")

            invoice_profile.frequency = InvoiceRecurringProfile.Frequencies.MONTHLY
            invoice_profile.day_of_month = frequency_day_of_month_int
        # endregion Monthly
        # region Yearly
        case "yearly":
            try:
                frequency_day_of_month_int = int(frequency_day_of_month)
                frequency_month_of_year_int = int(frequency_month_of_year)

                if frequency_day_of_month_int < -1 or frequency_day_of_month_int > 28:
                    raise ValueError

                if frequency_month_of_year_int < 1 or frequency_month_of_year_int > 12:
                    raise ValueError
            except ValueError:
                return ValidateFrequencyServiceResponse(error_message="Please select a valid day of the month and month of the year")

            invoice_profile.frequency = InvoiceRecurringProfile.Frequencies.YEARLY
            invoice_profile.day_of_month = frequency_day_of_month_int
            invoice_profile.month_of_year = frequency_month_of_year_int
        # endregion Yearly
        case _:
            return ValidateFrequencyServiceResponse(error_message="Invalid frequency")
    # endregion Match Frequency
    return ValidateFrequencyServiceResponse(success=True)
