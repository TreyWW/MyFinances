from datetime import datetime
from typing import Optional, List, Tuple
from decimal import Decimal
from django.db.models import Q
from .utils import round_currency
from backend.models import UserSubscription


def get_user_subscriptions(user, month: int, year: int) -> List[UserSubscription]:
    """Fetch user's subscription history for a specific month and year."""
    return UserSubscription.objects.filter(
        Q(start_date__year=year, start_date__month=month) | Q(end_date__isnull=True) | Q(end_date__year=year, end_date__month=month),
        user=user,
    ).order_by("start_date")


def get_highest_subscription_cost(subscriptions: List[UserSubscription]) -> Tuple[UserSubscription, Decimal]:
    """
    Find the highest subscription cost for the given month and return the subscription object and cost.
    """
    highest_subscription = max(
        subscriptions, key=lambda sub: sub.custom_subscription_price_per_month or sub.subscription_plan.price_per_month, default=None
    )

    if highest_subscription:
        cost = highest_subscription.custom_subscription_price_per_month or highest_subscription.subscription_plan.price_per_month
        return highest_subscription, cost

    return None, Decimal("0.00")
