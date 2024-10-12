import stripe

from backend.core.models import User, Organization
from billing.models import StripeWebhookEvent, UserSubscription


def subscription_ended(webhook_event: StripeWebhookEvent) -> None:
    event_data: stripe.Subscription = webhook_event.data.object
    stripe_customer = event_data.customer

    # Find the user or organization based on the stripe customer
    actor = (
        User.objects.filter(stripe_customer_id=stripe_customer).first()
        or Organization.objects.filter(stripe_customer_id=stripe_customer).first()
    )

    actor_subscription_plan = None

    if not actor:
        # If no user found, try to fetch the subscription plan using the stripe subscription ID
        plan = UserSubscription.objects.filter(
            stripe_subscription_id=event_data.id, stripe_subscription_id__isnull=False
        ).first()  # type: ignore[misc]

        if plan:
            actor_subscription_plan = plan
            actor = plan.owner
        else:
            print("Error: Could not find user or subscription plan.")
            return

    if not actor_subscription_plan:
        actor_subscriptions = UserSubscription.filter_by_owner(owner=actor).all()
        if not actor_subscriptions:
            return

        # Find a subscription plan with the same Stripe subscription ID
        if plan_with_same_id := actor_subscriptions.filter(stripe_subscription_id=event_data.id).first():
            plan_with_same_id.end_now()
