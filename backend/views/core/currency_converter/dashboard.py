import datetime

from django.http import HttpRequest
from django.shortcuts import render
from forex_python.converter import CurrencyRates

from backend.models import *


def convert_currency(init_currency, target_currency, amount, date=None):
    """
    Converts one currency to another, given an amount, using the forex_python library

    Parameters
    ----------
    init_currency : str, required
        The code for the initial currency to be converted

    target_currency : str, required
        The code for the target currency to be converted to

    amount : int or float, required
        The amount to be converted

    date: datetime, optional
        Past date at which the currency should be converted

    Returns
    ----------
    Returns an int or float representing the new amount
    """
    if not isinstance(init_currency, str) or len(init_currency) != 3:
        raise ValueError("Initial currency not recognized")

    if not isinstance(target_currency, str) or len(target_currency) != 3:
        raise ValueError("Target currency not recognized")

    if not isinstance(amount, (int, float)):
        raise ValueError("Amount is not an accepted datatype")

    if date is not None:
        if not isinstance(date, datetime.datetime):
            raise ValueError("Date is not an accepted datatype")

    if date is not None:
        # Check if date was a weekend
        # Forex's source has no records on weekends (5,6 = Sat, Sun)
        if date.weekday() >= 5:
            # move to friday before the weekend
            date = date.replace(day=date.day - (date.weekday() - 4))

    currency_rates = CurrencyRates()

    try:
        if date is not None:
            target_amount = currency_rates.convert(
                init_currency, target_currency, amount, date
            )
        else:
            target_amount = currency_rates.convert(
                init_currency, target_currency, amount
            )
        return round(target_amount, 2)
    except Exception as e:
        # Handle specific exceptions raised by forex_python if needed
        raise ValueError(f"Error in currency conversion: {e}")


def currency_conversion(request: HttpRequest):
    context = {}
    if request.method == "POST":
        print("Request was post")

        amount = request.POST["currency_amount"]
        try:
            amount = float(amount)
            converted_amt = convert_currency(
                request.POST["from_currency"],
                request.POST["to_currency"],
                amount,
            )
            original_currency_sign = UserSettings.CURRENCIES.get(
                request.POST["from_currency"], {}
            ).get("symbol", None)
            target_currency_sign = UserSettings.CURRENCIES.get(
                request.POST["to_currency"], {}
            ).get("symbol", None)

            context.update(
                {
                    "converted_amount": converted_amt,
                    "original_amount": amount,
                    "original_currency": request.POST["from_currency"],
                    "original_currency_sign": original_currency_sign,
                    "target_currency": request.POST["to_currency"],
                    "target_currency_sign": target_currency_sign,
                }
            )
        except Exception as e:
            print(f"exception raised in currency_conversion view: {e}")
    elif request.method == "GET":
        print("Request was get")

    usersettings, created = UserSettings.objects.get_or_create(user=request.user)

    context.update(
        {
            "currency_signs": usersettings.CURRENCIES,
        }
    )

    return render(
        request, "core/pages/currency_converter/dashboard.html", context=context
    )
