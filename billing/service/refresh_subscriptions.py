from datetime import datetime

import stripe
from django.db.models import QuerySet

from backend.models import User
from backend.types.requests import WebRequest
from billing.models import UserSubscription, SubscriptionPlan


def refresh_user_subscriptions(user: User):
    customer_id = user.stripe_customer_id

    user_subscriptions: QuerySet[UserSubscription] = UserSubscription.filter_by_owner(user).select_related("subscription_plan")

    # Just to get the customer_id
    if not customer_id and user_subscriptions.exists():
        for subscription in user_subscriptions.all():
            try:
                s: stripe.Subscription = stripe.Subscription.retrieve(subscription.stripe_subscription_id)

                customer_id = s.customer
                user.stripe_customer_id = customer_id
                user.save()
            except stripe.error.InvalidRequestError:
                continue
        if not customer_id:
            return

    all_active_subscriptions = stripe.Subscription.list(customer=customer_id, status="active").data

    all_subscriptions = stripe.Subscription.list(customer=customer_id).data

    active_subscriptions_by_id: dict[str, stripe._subscription.Subscription] = {
        subscription.id: subscription for subscription in all_active_subscriptions
    }

    all_subscriptions_by_id = {subscription.id: subscription for subscription in all_subscriptions}

    for subscription in user_subscriptions.filter(end_date__isnull=True):
        if active_subscriptions_by_id.get(subscription.stripe_subscription_id):
            del active_subscriptions_by_id[subscription.stripe_subscription_id]  # don't worry about it as it is active
        elif all_subscriptions_by_id.get(subscription.stripe_subscription_id):
            subscription.end_date = datetime.fromtimestamp(all_subscriptions_by_id[subscription.stripe_subscription_id].current_period_end)
            subscription.save()
        else:
            subscription.end_now()

    for subscription_id, subscription in active_subscriptions_by_id.items():
        plan: SubscriptionPlan = SubscriptionPlan.objects.filter(stripe_product_id=subscription.plan.product).first()

        if not plan:
            continue

        UserSubscription.objects.create(
            owner=user,
            subscription_plan=plan,
            stripe_subscription_id=subscription_id,
            start_date=subscription.current_period_start,
        )

    return
