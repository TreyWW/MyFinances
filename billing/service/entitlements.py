import stripe.entitlements
from django.contrib import messages
from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient
from django.shortcuts import redirect

from backend.models import User, Organization
from billing.models import StripeWebhookEvent
from billing.service.get_user import get_actor_from_stripe_customer

cache: RedisCacheClient = cache


def entitlements_updated_via_stripe_webhook(webhook_event: StripeWebhookEvent) -> None:
    data: stripe.entitlements.ActiveEntitlementSummary = webhook_event.data["object"]
    actor = get_actor_from_stripe_customer(data["customer"])

    if not actor:
        print("No actor found for customer.")
        return

    # Re-fetch and update the entitlements for the actor (User or Organization)
    update_user_entitlements(actor)


def update_user_entitlements(actor: User | Organization) -> list[str]:
    if not actor.stripe_customer_id:
        return []

    entitlements = stripe.entitlements.ActiveEntitlement.list(customer=actor.stripe_customer_id, limit=25).data

    entitlement_names = [entitlement.lookup_key for entitlement in entitlements]

    actor.entitlements = entitlement_names
    actor.save(update_fields=["entitlements"])

    cache_actor_type = "user" if isinstance(actor, User) else "org"

    cache.set(f"myfinances:entitlements:{cache_actor_type}:{actor.id}", entitlement_names, timeout=3600)

    return entitlement_names


def get_entitlements(actor: User | Organization, avoid_cache=False) -> list[str]:
    cache_key = "user" if isinstance(actor, User) else "org"

    if not avoid_cache and (cached_entitlements := cache.get(f"myfinances:entitlements:{cache_key}:{actor.id}", default=[])):
        return cached_entitlements
    return update_user_entitlements(actor)


def has_entitlement(actor: User | Organization, entitlement: str) -> bool:
    return entitlement in get_entitlements(actor)


def has_entitlements(actor: User | Organization, entitlements: list[str]) -> bool:
    return all(entitlement in entitlements for entitlement in get_entitlements(actor))
