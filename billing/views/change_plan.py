import logging

import stripe
from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from backend.decorators import htmx_only, web_require_scopes
from backend.core.models import User
from backend.core.types.requests import WebRequest
from billing.models import SubscriptionPlan, UserSubscription, StripeCheckoutSession
from billing.service.stripe_customer import get_or_create_customer_id

logger = logging.getLogger(__name__)


@web_require_scopes("billing:manage", api=True, htmx=True)
@htmx_only("billing:dashboard")
def change_plan_endpoint(request: WebRequest):

    plan: SubscriptionPlan | None = None

    if plan_filter := request.POST.get("plan_name"):
        plan = SubscriptionPlan.objects.filter(name=plan_filter).first()
    elif plan_filter := request.POST.get("plan_id"):
        plan = SubscriptionPlan.objects.filter(id=plan_filter).first()

    if not plan:
        messages.error(request, "Invalid plan")
        return render(request, "base/toast.html")
    elif plan.price_per_month == -1 or plan.name.lower() == "enterprise":
        print("THIS PLAN IS ENTERPRISE, currently not implemented")
        messages.error(request, "Invalid plan (not yet implemented)")
        return render(request, "base/toast.html")

    users_plans: QuerySet[UserSubscription] = UserSubscription.filter_by_owner(request.actor)

    if plan.price_per_month == 0 and users_plans.exists():
        messages.error(
            request,
            """
            Unfortunately you have already used up your free trial. Please upgrade to a paid plan to continue.
            If you have another query, feel free to book a call with the project lead + founder!
            <a class="link link-primary" href="https://cal.com/d/88aZVDH9EScpNQnMp4WjEg/myfinances-consumer-call"
                onclick="const e = arguments[0] || window.event; e.stopPropagation();" target=”_blank”>
                <strong>Book here</strong>
            </a>
        """,
        )
        return render(request, "base/toast.html", {"autohide": False})

    users_active_plans: QuerySet[UserSubscription] = users_plans.filter(end_date__isnull=True)
    # if users_active_plans.exists():
    #     for active_plan in users_active_plans:
    #         active_plan.end_date = timezone_now()
    #         active_plan.save()

    line_items = [{"adjustable_quantity": {"enabled": False}, "quantity": 1, "price": plan.stripe_price_id}]  # type: ignore

    checkout_session_django_object = (
        StripeCheckoutSession.objects.create(user=request.actor, plan=plan)
        if isinstance(request.actor, User)
        else StripeCheckoutSession.objects.create(organization=request.actor, plan=plan)
    )

    for feature in plan.features.all():
        if not feature.stripe_price_id:
            continue

        checkout_session_django_object.features.add(feature)

        line_items.append(
            {
                # "adjustable_quantity": {
                #     "enabled": False
                # },
                "price": feature.stripe_price_id,
                # "quantity": 1,
            }
        )

    customer_id = get_or_create_customer_id(request.actor)

    if isinstance(request.actor, User):
        customer_email = request.actor.email
    else:
        customer_email = request.actor.leader.email

    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        customer_email=customer_email if not customer_email else None,  # type: ignore[arg-type]
        line_items=line_items,  # type: ignore[arg-type]
        mode="subscription",
        # return_url="http://127.0.0.1:8000" + reverse("billing:stripe_checkout_failed_response"),
        cancel_url=request.build_absolute_uri(reverse("billing:dashboard")),
        success_url=request.build_absolute_uri(reverse("billing:stripe_checkout_success_response")),
        metadata={"dj_checkout_uuid": checkout_session_django_object.uuid, "dj_subscription_plan_id": str(plan.id)},
        saved_payment_method_options={"payment_method_save": "enabled"},
    )

    checkout_session_django_object.stripe_session_id = checkout_session.id

    checkout_session_django_object.save()

    # UserSubscription.objects.create(owner=request.actor, subscription_plan=plan)
    messages.success(request, "Great! Redirecting you to stripe now!")
    r = HttpResponse(status=200)
    r["HX-Redirect"] = str(checkout_session.url)
    return r
