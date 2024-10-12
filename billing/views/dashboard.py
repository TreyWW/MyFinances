from django.shortcuts import render

from backend.decorators import web_require_scopes
from billing.models import UserSubscription, SubscriptionPlan
from backend.core.types.requests import WebRequest


@web_require_scopes("billing:manage", api=True, htmx=True)
def billing_dashboard_endpoint(request: WebRequest):
    context: dict = {}

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
        "pages/billing/dashboard/dashboard.html",
        context,
    )


@web_require_scopes("billing:manage", api=True, htmx=True)
def all_subscriptions_htmx_endpoint(request: WebRequest):
    context: dict = {}

    subscriptions = UserSubscription.filter_by_owner(request.actor).select_related("subscription_plan").all()

    context.update(
        {
            "active_subscription": subscriptions.filter(end_date__isnull=True).first(),
            "all_user_subscriptions": subscriptions,
        }
    )

    return render(
        request,
        "pages/billing/dashboard/all_subscriptions.html",
        context,
    )
