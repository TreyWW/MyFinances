from django.shortcuts import render
from django.utils import timezone

from backend.types.requests import WebRequest
from backend.service.billing.calculate.test import generate_monthly_billing_summary


def billing_dashboard_endpoint(request: WebRequest):
    return render(
        request,
        "pages/billing/dashboard.html",
        {
            "current_month": timezone.now().month,
            "current_year": timezone.now().year,
            "months": [
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
            ],
        },
    )
