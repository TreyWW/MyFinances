import stripe
from typing import Union
from django.utils import timezone

from backend.models import Organization
from billing.models import UserSubscription, SubscriptionPlan
from django.contrib.auth.models import User

from billing.service.entitlements import update_user_entitlements


def create_subscription(owner: Union[User, Organization], subscription_plan: SubscriptionPlan) -> UserSubscription:
    """
    Creates a new Stripe subscription for a user or organization.

    Args:
        owner: The user or organization subscribing.
        subscription_plan: The plan the owner is subscribing to.

    Returns:
        A UserSubscription object representing the subscription.
    """
    # Create a new Stripe subscription for the given owner (user or organization)
    stripe_subscription = stripe.Subscription.create(
        customer=owner.stripe_customer_id,
        items=[{"price": subscription_plan.stripe_price_id}],
    )

    # Create the corresponding UserSubscription record in your database
    user_subscription = UserSubscription.objects.create(
        owner=owner, subscription_plan=subscription_plan, stripe_subscription_id=stripe_subscription.id, start_date=timezone.now()
    )

    # Update user entitlements via Stripe entitlements
    update_user_entitlements(owner)

    return user_subscription


def cancel_subscription(user_subscription: UserSubscription) -> UserSubscription:
    """
    Cancels an active Stripe subscription and updates the local subscription record.

    Args:
        user_subscription: The subscription to cancel.

    Returns:
        The updated UserSubscription object with the end_date set.
    """
    stripe.Subscription.delete(subscription=user_subscription.stripe_subscription_id)

    # Mark the subscription as canceled in your local database
    user_subscription.end_date = timezone.now()
    user_subscription.save()

    # Update entitlements after cancellation
    update_user_entitlements(user_subscription.owner)

    return user_subscription


def handle_plan_change(user_subscription: UserSubscription, new_plan: SubscriptionPlan) -> UserSubscription:
    """
    Updates the user's Stripe subscription to a new plan, with proration handled automatically.

    Args:
        user_subscription: The current UserSubscription to update.
        new_plan: The new SubscriptionPlan to switch to.

    Returns:
        The updated UserSubscription object with the new plan.
    """
    stripe.Subscription.modify(
        user_subscription.stripe_subscription_id,
        cancel_at_period_end=False,  # Cancels the current plan immediately
        items=[{"price": new_plan.stripe_price_id}],
    )

    # Update the local subscription model
    user_subscription.subscription_plan = new_plan
    user_subscription.save()

    # Update entitlements after the plan change
    update_user_entitlements(user_subscription.owner)

    return user_subscription
