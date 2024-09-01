import stripe
from django.http import HttpResponse
from django.shortcuts import redirect

from backend.types.requests import WebRequest
from billing.models import UserSubscription, SubscriptionPlan
from billing.service.refresh_subscriptions import refresh_user_subscriptions


def refetch_subscriptions_endpoint(request: WebRequest):
    refresh_user_subscriptions(request.user)

    if request.htmx:
        response = HttpResponse()
        response["HX-Refresh"] = "true"
        return response
    return redirect("billing:dashboard")
