import time

from django import template

register = template.Library()


def split(string, char=" "):
    return string.split(char)


def dashify(string, recurrence=2):
    num_str = str(string)

    return "-".join(num_str[i : i + recurrence] for i in range(0, len(num_str), recurrence))


def to_list(string, separator=",") -> list[str]:
    return string.split(separator)


def contains(value, arg):
    return arg in str(value)


def day_to_number_sunday(day: str) -> int:
    """
    Converts a day of the week to a number with Sunday as the first day.

    Args:
        day (str): The day of the week (e.g., "Sunday", "Monday").

    Returns:
        int: The corresponding number with Sunday as 0 and Saturday as 6.
    """
    # Get the day number with Monday as 0
    day_number = time.strptime(day, "%A").tm_wday

    # Adjust the day number to make Sunday the first day
    sunday_first_day_number = (day_number + 1) % 7

    return sunday_first_day_number


def day_to_number_monday(day: str) -> int:
    return time.strptime(day, "%A").tm_wday + 1


def month_to_number(month: str) -> int:
    return time.strptime(month, "%B").tm_mon


register.filter("split", split)
register.filter("dashify", dashify)
register.filter("contains", contains)
register.filter("to_list", to_list)
register.filter("day_to_number_monday", day_to_number_monday)
register.filter("day_to_number_sunday", day_to_number_sunday)
register.filter("month_to_number", month_to_number)
