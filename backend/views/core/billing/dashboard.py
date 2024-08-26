from django.shortcuts import render
from django.utils import timezone

from backend.types.requests import WebRequest
from backend.service.billing.calculate.test import generate_monthly_billing_summary


def billing_dashboard_endpoint(request: WebRequest):

    billing_dict: dict = generate_monthly_billing_summary(request.user, timezone.now().month, timezone.now().year)

    return render(request, "pages/billing/dashboard.html", {"billing": billing_dict})
