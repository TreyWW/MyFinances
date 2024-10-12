from backend.core.utils.dataclasses import BaseServiceResponse
from datetime import date as Date


class MonthlyCronServiceResponse(BaseServiceResponse[str]): ...


class WeeklyCronServiceResponse(BaseServiceResponse[str]): ...


class YearlyCronServiceResponse(BaseServiceResponse[str]): ...


class CronServiceResponse(BaseServiceResponse[str]): ...


def get_monthly_cron(day_of_month: int | None = None, date: Date | None = None) -> MonthlyCronServiceResponse:
    if day_of_month:
        cron_expression = f"0 7 {day_of_month} * ? *"
        return MonthlyCronServiceResponse(True, cron_expression)
    elif date:
        cron_expression = f"0 7 {date.day} {date.month} ? *"
        return MonthlyCronServiceResponse(True, cron_expression)
    else:
        return MonthlyCronServiceResponse(False, "", "Invalid input for monthly cron")


def get_weekly_cron(day_of_week: int | None = None) -> WeeklyCronServiceResponse:
    if isinstance(day_of_week, int) and 0 <= day_of_week <= 6:
        cron_expression = f"0 7 ? * {day_of_week + 1} *"
        return WeeklyCronServiceResponse(True, cron_expression)
    else:
        return WeeklyCronServiceResponse(False, "", "Invalid input for weekly cron")


def get_yearly_cron(day_of_month: int, month: int) -> YearlyCronServiceResponse:
    if 1 <= day_of_month <= 31 and 1 <= month <= 12:
        cron_expression = f"0 7 {day_of_month} {month} ? *"
        return YearlyCronServiceResponse(True, cron_expression)
    else:
        return YearlyCronServiceResponse(False, "", "Invalid input for yearly cron")


def get_schedule_cron(
    frequency: str, day_of_month: int | None = None, day_of_week: int | None = None, month: int | None = None, date: Date | None = None
) -> CronServiceResponse:
    """
    Generates a cron expression for AWS EventBridge based on the specified frequency.

    Args:
        frequency (str): The frequency of the schedule. It can be "monthly", "weekly", or "yearly".
        day_of_month (int, optional): The day of the month for the schedule. Required for monthly and yearly frequencies.
        day_of_week (int, optional): The day of the week for the schedule (0 for Sunday, 6 for Saturday). Required for weekly frequency.
        month (int, optional): The month of the schedule (1 for January, 12 for December). Required for yearly frequency.
        date (datetime.date, optional): The specific date for the schedule. Can be used for monthly frequency instead of day_of_month.

    Returns:
        CronServiceResponse: The response containing the cron expression or an error message.

    Examples:
        - Monthly schedule on the 15th day of each month:
            get_schedule_cron(frequency="monthly", day_of_month=15)

        - Weekly schedule on every Tuesday (2nd day of the week):
            get_schedule_cron(frequency="weekly", day_of_week=2)

        - Yearly schedule on the 15th of January:
            get_schedule_cron(frequency="yearly", day_of_month=15, month=1)
    """

    response: MonthlyCronServiceResponse | YearlyCronServiceResponse | WeeklyCronServiceResponse

    if frequency == "monthly":
        response = get_monthly_cron(day_of_month, date)
    elif frequency == "weekly":
        response = get_weekly_cron(day_of_week)
    elif frequency == "yearly":
        if day_of_month is not None and month is not None:
            response = get_yearly_cron(day_of_month, month)
        else:
            response = YearlyCronServiceResponse(False, "", "Day of month and month are required for yearly frequency")
    else:
        return CronServiceResponse(False, "", "Invalid frequency type")

    if response.success:
        return CronServiceResponse(True, response.response)
    else:
        return CronServiceResponse(False, "", response.error)
