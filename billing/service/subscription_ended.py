import stripe

from backend.models import User
from billing.models import StripeWebhookEvent, UserSubscription


def subscription_ended(webhook_event: StripeWebhookEvent) -> None:
    event_data: stripe.Subscription = webhook_event.data.object
    stripe_customer = event_data.customer

    user = User.objects.filter(stripe_customer_id=stripe_customer).first()
    user_subscription_plan = None

    if not user:
        plan = UserSubscription.objects.filter(stripe_subscription_id=event_data.id, stripe_subscription_id__isnull=False).first()

        if plan:
            user_subscription_plan = plan
            user = plan.owner  # Assuming 'owner' links to the user or org
        else:
            print("Error: Could not find user or subscription plan.")
            return

    if not user_subscription_plan:
        user_subscriptions = UserSubscription.objects.filter(owner=user).all()
        if not user_subscriptions:
            return

        # Find a subscription plan with the same Stripe subscription ID
        if plan_with_same_id := user_subscriptions.filter(stripe_subscription_id=event_data.id).first():
            plan_with_same_id.end_now()
