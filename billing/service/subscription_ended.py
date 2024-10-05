import stripe

from backend.models import User
from billing.models import StripeWebhookEvent, UserSubscription


def subscription_ended(webhook_event: StripeWebhookEvent):
    event_data: stripe.Subscription = webhook_event.data["object"]
    stripe_customer_id = event_data["customer"]

    # Try to find the user or organization by stripe_customer_id
    user = User.objects.filter(stripe_customer_id=stripe_customer_id).first()

    if not user:
        plan = UserSubscription.objects.filter(stripe_subscription_id=event_data.id, stripe_subscription_id__isnull=False).first()

        if plan:
            user_subscription_plan = plan
            user = plan.owner
        else:
            print("Error: Could not find user or plan for subscription deletion.")
            return

    # Handle ending subscriptions
    user_subscription_plan = UserSubscription.objects.filter(stripe_subscription_id=event_data.id).first()
    if user_subscription_plan:
        user_subscription_plan.end_now()
