import stripe

from backend.core.utils.calendar import timezone_now
from billing.models import StripeCheckoutSession, StripeWebhookEvent, UserSubscription


def checkout_completed(webhook_event: StripeWebhookEvent):
    event_data: stripe.checkout.Session = webhook_event.data["object"]

    stripe_session_obj = StripeCheckoutSession.objects.filter(
        uuid=event_data.metadata.get("dj_checkout_uuid", "doesn't_exist") if event_data.metadata else "doesn't_exist"
    ).first()  # type: ignore[misc]

    if not stripe_session_obj:
        print("No matching session object found.")
        return

    completed_with_session_object(stripe_session_obj, event_data)


def completed_with_session_object(stripe_session_obj: StripeCheckoutSession, event_data: stripe.checkout.Session) -> None:
    # Fetch current active subscriptions based on the owner (user or organization)
    user_current_plans = UserSubscription.filter_by_owner(owner=stripe_session_obj.owner).filter(end_date__isnull=True)

    # Get plan ID from metadata
    stripe_plan_id = event_data.metadata.get("dj_subscription_plan_id", None) if event_data.metadata else None
    if not stripe_plan_id:
        print("No subscription plan ID found in metadata.")
        return

    # Cancel existing subscriptions except the one in the metadata
    for current_plan in user_current_plans:
        if current_plan.subscription_plan.id != stripe_plan_id:  # Fix: Using `subscription_plan.id`
            stripe.Subscription.modify(current_plan.stripe_subscription_id, cancel_at_period_end=True)  # type: ignore[arg-type]
            current_plan.end_date = timezone_now()
            current_plan.save()

    # Create new subscription if the user doesn't have it
    if not user_current_plans.filter(subscription_plan__id=stripe_plan_id).exists():  # Fix: Using `subscription_plan__id`
        UserSubscription.objects.create(
            owner=stripe_session_obj.owner,
            subscription_plan_id=stripe_plan_id,
            stripe_subscription_id=event_data.subscription,
        )

    # Expire the checkout session
    stripe.checkout.Session.expire(stripe_session_obj.stripe_session_id)  # type: ignore[arg-type]
    stripe_session_obj.delete()
