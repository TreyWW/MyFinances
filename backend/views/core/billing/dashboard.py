from django.shortcuts import render

from backend.models import UserSubscription, SubscriptionPlan
from backend.types.requests import WebRequest
from backend.utils.calendar import get_months_text, timezone_now


def billing_dashboard_endpoint(request: WebRequest):

    months = get_months_text()

    subscriptions = UserSubscription.filter_by_owner(request.actor).all()
    all_subscription_plans = SubscriptionPlan.objects.all()

    return render(
        request,
        "pages/billing/dashboard.html",
        {
            "current_month": {"text": months[timezone_now().month - 1], "int": timezone_now().month},
            "current_year": timezone_now().year,
            "months": months,
            "subscriptions": subscriptions,
            "active_subscription": subscriptions.filter(end_date__isnull=True).first(),
            "all_subscription_plans": all_subscription_plans,
        },
    )
