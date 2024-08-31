import stripe

from backend.utils.calendar import timezone_now
from billing.models import StripeCheckoutSession, StripeWebhookEvent, PlanFeature, UserSubscription, SubscriptionPlan


def checkout_completed(webhook_event: StripeWebhookEvent):
    event_data: stripe.checkout.Session = webhook_event.data.object

    stripe_session_obj = StripeCheckoutSession.objects.filter(uuid=event_data.metadata.get("dj_checkout_uuid")).first()

    if stripe_session_obj:
        completed_with_session_object(stripe_session_obj, event_data)


def completed_with_session_object(stripe_session_obj: StripeCheckoutSession, event_data: stripe.checkout.Session):
    USER_CURRENT_PLANS = UserSubscription.objects.filter(user=stripe_session_obj.user, end_date__isnull=True).all()

    STRIPE_META_DJ_SUBSCRIPTION_PLAN_ID = event_data.metadata.get("dj_subscription_plan_id", "doesn't_exist")

    for current_plan in USER_CURRENT_PLANS:
        if current_plan.subscription_plan_id == STRIPE_META_DJ_SUBSCRIPTION_PLAN_ID:
            continue

        stripe.Subscription.cancel(current_plan.stripe_subscription_id)

        current_plan.end_date = timezone_now()
        current_plan.save()

    if not USER_CURRENT_PLANS.filter(subscription_plan_id=STRIPE_META_DJ_SUBSCRIPTION_PLAN_ID).exists():
        new_plan = UserSubscription.objects.create(
            user=stripe_session_obj.user,
            subscription_plan_id=STRIPE_META_DJ_SUBSCRIPTION_PLAN_ID,
            stripe_subscription_id=event_data.subscription,
        )

    stripe.checkout.Session.expire(stripe_session_obj.stripe_session_id)

    stripe_session_obj.delete()

    return
