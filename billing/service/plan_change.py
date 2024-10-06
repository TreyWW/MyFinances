from datetime import datetime
import stripe
from django.db.models import QuerySet
from backend.models import User, Organization
from billing.models import UserSubscription, SubscriptionPlan
from billing.service.entitlements import update_user_entitlements
from billing.service.stripe_customer import get_or_create_customer_id


def handle_plan_change(user_subscription: UserSubscription, new_plan: SubscriptionPlan) -> UserSubscription:
    """
    Handles plan upgrades or downgrades.
    """
    # Cancel the current Stripe subscription if necessary
    stripe.Subscription.modify(
        user_subscription.stripe_subscription_id,
        cancel_at_period_end=False,  # Cancels immediately
    )

    # Create a new Stripe subscription for the new plan
    new_subscription = stripe.Subscription.create(
        customer=user_subscription.owner.stripe_customer_id,
        items=[{"price": new_plan.stripe_price_id}],
    )

    # Update the UserSubscription object with new plan and subscription id
    user_subscription.subscription_plan = new_plan
    user_subscription.stripe_subscription_id = new_subscription.id
    user_subscription.save()

    return user_subscription
