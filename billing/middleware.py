from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import resolve

from backend.core.types.requests import WebRequest
from billing.billing_settings import NO_SUBSCRIPTION_PLAN_DENY_VIEW_NAMES
from billing.models import UserSubscription


# middleware to check if user is subscribed to a plan yet


class CheckUserSubScriptionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: WebRequest):
        if not request.user.is_authenticated:
            return self.get_response(request)

        if request.team:
            # todo: handle organization billing
            return self.get_response(request)

        subscription: UserSubscription | None = (
            UserSubscription.filter_by_owner(request.actor).filter(end_date__isnull=True).prefetch_related("subscription_plan").first()
        )
        request.users_subscription = subscription

        resolver_match = resolve(request.path_info)

        view_name = resolver_match.view_name

        if view_name not in NO_SUBSCRIPTION_PLAN_DENY_VIEW_NAMES:
            return self.get_response(request)

        if not subscription:
            print("[BILLING] [MIDDLEWARE] User doesn't have an active subscription.")
            messages.warning(
                request,
                """
                You currently are not subscribed to a plan. If you think this is a mistake scroll down and
                press "Refetch" or contact support at
                <a href="mailto:support@strelix.org" class="link link-primary font-extrabold">support@strelix.org</a>.""",
            )

            if request.htmx:
                return render(request, "base/toast.html", {"autohide": False})
            return redirect("billing:dashboard")
        return self.get_response(request)
