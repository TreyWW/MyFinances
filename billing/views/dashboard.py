from django.shortcuts import render

from billing.models import UserSubscription, SubscriptionPlan
from backend.types.requests import WebRequest
from backend.utils.calendar import get_months_text, timezone_now


def billing_dashboard_endpoint(request: WebRequest):
    context: dict = {}
    months = get_months_text()

    subscriptions = UserSubscription.filter_by_owner(request.actor).select_related("subscription_plan").all()
    all_subscription_plans = SubscriptionPlan.objects.all()

    if subscriptions.exists():
        context["free_plan_available"] = True

    context.update(
        {
            "active_subscription": subscriptions.filter(end_date__isnull=True).first(),
            "all_user_subscriptions": subscriptions,
            "all_subscription_plans": all_subscription_plans,
        }
    )

    return render(
        request,
        "pages/billing/dashboard.html",
        context,
    )
