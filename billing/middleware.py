import os

import stripe
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse, resolve

from backend.types.requests import WebRequest
from billing.models import UserSubscription, SubscriptionPlan


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

        subscription: UserSubscription = (
            UserSubscription.filter_by_owner(request.actor).filter(end_date__isnull=True).prefetch_related("subscription_plan").first()
        )
        request.users_subscription = subscription

        resolver_match = resolve(request.path_info)

        view_name = resolver_match.view_name

        if view_name in ["billing:dashboard", "billing:stripe_customer_portal", "billing:change_plan"] or request.path.startswith("/admin"):
            return self.get_response(request)

        if not subscription:
            print("[BILLING] [MIDDLEWARE] User doesn't have an active subscription. Checking stripe.")

            if not request.user.stripe_customer_id:
                request.user.stripe_customer_id = stripe.Customer.create(
                    name=request.user.get_full_name(), email=request.user.email, metadata={"dj_user_id": str(request.user.id)}
                ).id
                request.user.save(update_fields=["stripe_customer_id"])

            customer_stripe_subscriptions = stripe.Subscription.list(customer=request.user.stripe_customer_id)

            has_existing_stripe_subscription = len(customer_stripe_subscriptions.data) > 0

            if has_existing_stripe_subscription:
                stripe_product_id = customer_stripe_subscriptions.data[0]["items"].data[0].plan.product

                plan = SubscriptionPlan.objects.filter(stripe_product_id=stripe_product_id).first()

                if not plan:
                    print(f"{stripe_product_id} not found in SubscriptionPlans!")
                    return self.get_response(request)

                request.users_subscription = UserSubscription.objects.create(
                    owner=request.user, subscription_plan=plan, stripe_subscription_id=customer_stripe_subscriptions.data[0].id
                )
                return self.get_response(request)

            messages.warning(request, "You currently are not subscribed to a plan. Get started today!")
            return redirect("billing:dashboard")
        return self.get_response(request)
