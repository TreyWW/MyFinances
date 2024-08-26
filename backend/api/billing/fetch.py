from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.http import require_GET

from backend.decorators import htmx_only
from backend.service.billing.calculate.test import generate_monthly_billing_summary
from backend.types.requests import WebRequest

from django.shortcuts import render


@require_GET
@htmx_only("billing:dashboard")
def fetch_bill_table_by_month_endpoint(request: WebRequest):
    month = request.GET.get("month", timezone.now().month)
    year = request.GET.get("year", timezone.now().year)

    try:
        month = int(month)
        year = int(year)
    except ValueError:
        messages.error(request, "Invalid month or year")
        return render(request, "base/toast.html")

    billing_dict: dict = generate_monthly_billing_summary(request.user, month, year)

    return render(
        request,
        "pages/billing/table_body.html",
        {"billing": billing_dict, "month": month, "year": year},
    )
