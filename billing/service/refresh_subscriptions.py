from datetime import datetime
import stripe
from django.db.models import QuerySet
from backend.models import User, Organization
from billing.models import UserSubscription, SubscriptionPlan
from billing.service.entitlements import update_user_entitlements
from billing.service.stripe_customer import get_or_create_customer_id


def retrieve_stripe_subscription(subscription_id: str) -> stripe.Subscription | None:
    """Retrieve a Stripe subscription given its ID."""
    try:
        return stripe.Subscription.retrieve(subscription_id)
    except stripe.InvalidRequestError:
        return None


def find_customer_id(user_subscriptions: QuerySet[UserSubscription], actor: User | Organization) -> str | None:
    """Find or retrieve the Stripe customer ID from user subscriptions."""
    for subscription in user_subscriptions:
        if not subscription.stripe_subscription_id:
            continue

        stripe_subscription = retrieve_stripe_subscription(subscription.stripe_subscription_id)
        if stripe_subscription:
            stripe_customer = stripe_subscription.customer if isinstance(stripe_subscription.customer, str) else None
            actor.stripe_customer_id = stripe_customer
            actor.save()
            return stripe_customer

    return None


def get_active_stripe_subscriptions(customer_id: str) -> dict[str, stripe.Subscription]:
    """Retrieve all active Stripe subscriptions for a customer."""
    return {subscription.id: subscription for subscription in stripe.Subscription.list(customer=customer_id, status="active").data}


def get_all_stripe_subscriptions(customer_id: str) -> dict[str, stripe.Subscription]:
    """Retrieve all Stripe subscriptions for a customer."""
    return {subscription.id: subscription for subscription in stripe.Subscription.list(customer=customer_id).data}


def update_existing_subscriptions(user_subscriptions: QuerySet[UserSubscription], all_subscriptions_by_id: dict[str, stripe.Subscription]):
    """Update user subscriptions based on existing Stripe data."""
    for subscription in user_subscriptions.filter(end_date__isnull=True):
        stripe_subscription = (
            all_subscriptions_by_id.get(subscription.stripe_subscription_id) if subscription.stripe_subscription_id else None
        )
        if stripe_subscription:
            subscription.end_date = datetime.fromtimestamp(stripe_subscription.current_period_end)
            subscription.save()
        else:
            subscription.end_now()


def create_missing_subscriptions(actor: User | Organization, active_subscriptions_by_id: dict[str, stripe.Subscription]):
    """Create user subscriptions in the database for active Stripe subscriptions not already tracked."""
    for subscription_id, subscription_active in active_subscriptions_by_id.items():
        if hasattr(subscription_active, "items") and getattr(subscription_active.items, "data", None):
            stripe_product_id = subscription_active.items.data[0].plan.product

            plan = SubscriptionPlan.objects.filter(stripe_product_id=stripe_product_id).first()

            if plan:
                UserSubscription.objects.create(
                    owner=actor,
                    subscription_plan=plan,
                    stripe_subscription_id=subscription_id,
                )


def refresh_actor_subscriptions(actor: User | Organization):
    """Refresh subscriptions for an actor by syncing with Stripe."""
    customer_id = get_or_create_customer_id(actor)
    if not customer_id:
        return  # Exit if no valid customer ID found

    user_subscriptions = UserSubscription.filter_by_owner(actor).select_related("subscription_plan")

    active_subscriptions_by_id = get_active_stripe_subscriptions(customer_id)
    all_subscriptions_by_id = get_all_stripe_subscriptions(customer_id)

    # Update or close existing subscriptions
    update_existing_subscriptions(user_subscriptions, all_subscriptions_by_id)

    # Create new subscriptions for active Stripe subscriptions not in the database
    create_missing_subscriptions(actor, active_subscriptions_by_id)

    # Update user entitlements after syncing subscriptions
    update_user_entitlements(actor)
