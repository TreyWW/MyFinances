import datetime

from django.utils import timezone


def get_months_text() -> list[str]:
    return [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]


def timezone_now() -> datetime.datetime:
    return timezone.now()
