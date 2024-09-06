import stripe

from backend.models import User
from billing.models import StripeWebhookEvent, UserSubscription


def subscription_ended(webhook_event: StripeWebhookEvent):
    event_data: stripe.Subscription = webhook_event.data.object

    stripe_customer = event_data.customer

    user: User | None = User.objects.filter(stripe_customer_id=stripe_customer).first()
    user_subscription_plan: UserSubscription | None = None

    if not user:
        plan: UserSubscription | None = UserSubscription.objects.filter(
            stripe_subscription_id=event_data.id, stripe_subscription_id__isnull=False
        ).first()

        if plan:
            user_subscription_plan = plan
            user = plan.user
        else:
            print("SOMETHING WENT WRONG: COULD NOT FIND PLAN OR USER")
            return

    if not user_subscription_plan:
        USERS_PLANS = UserSubscription.objects.filter(user=user).all()

        if not USERS_PLANS:
            return

        if plan_with_same_id := USERS_PLANS.filter(stripe_subscription_id=event_data.id).first():
            plan_with_same_id.end_now()
