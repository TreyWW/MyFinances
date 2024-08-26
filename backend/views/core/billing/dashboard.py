from django.shortcuts import render

from backend.types.requests import WebRequest
from backend.utils.calendar import get_months_text, timezone_now


def billing_dashboard_endpoint(request: WebRequest):

    months = get_months_text()

    return render(
        request,
        "pages/billing/dashboard.html",
        {
            "current_month": {"text": months[timezone_now().month - 1], "int": timezone_now().month},
            "current_year": timezone_now().year,
            "months": months,
        },
    )
