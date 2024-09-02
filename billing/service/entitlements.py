import stripe.entitlements
from django.contrib import messages
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient
from django.shortcuts import redirect

from backend.models import User
from billing.models import StripeWebhookEvent
from billing.service.get_user import get_user_from_stripe_customer

cache: RedisCacheClient


def entitlements_updated_via_stripe_webhook(webhook_event: StripeWebhookEvent) -> None:
    data: stripe.entitlements.ActiveEntitlementSummary = webhook_event.data.object

    user = get_user_from_stripe_customer(data.customer)

    if not user:
        return

    update_user_entitlements(user)  # we fully re-fetch as the summary object contains a max of 10 items, so just in case we fetch ALL

    return None


def update_user_entitlements(user: User) -> list[str]:
    if not user.stripe_customer_id:
        return []

    entitlements = stripe.entitlements.ActiveEntitlement.list(customer=user.stripe_customer_id, limit=25).data

    entitlement_names = [entitlement.lookup_key for entitlement in entitlements]

    user.entitlements = entitlement_names
    user.save(update_fields=["entitlements"])

    cache.set(f"myfinances:entitlements:user:{user.id}", entitlement_names, timeout=3600)

    return entitlement_names


def get_entitlements(user: User) -> list[str]:
    if cached_entitlements := cache.get(f"myfinances:entitlements:user:{user.id}", default=[]):
        return cached_entitlements
    return update_user_entitlements(user)


def has_entitlement(user: User, entitlement: str) -> bool:
    return entitlement in get_entitlements(user)


def has_entitlements(user: User, entitlements: list[str]) -> bool:
    return all(entitlement in entitlements for entitlement in get_entitlements(user))
