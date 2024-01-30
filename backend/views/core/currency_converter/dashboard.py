import datetime

from django.http import HttpRequest
from django.shortcuts import render
from forex_python.converter import CurrencyRates

from backend.models import *


def currency_convert_view(request: HttpRequest):
    context = {}

    usersettings, created = UserSettings.objects.get_or_create(user=request.user)

    context.update(
        {
            "currency_signs": usersettings.CURRENCIES,
        }
    )

    return render(request, "pages/currency_converter/dashboard.html", context=context)
