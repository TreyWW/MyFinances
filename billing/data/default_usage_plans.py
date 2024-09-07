from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass
class DefaultFeature:
    """
    Single Product, e.g. "invoices-created"
    This is a stripe "PRICE" (part of a PRODUCT)
    """

    slug: str  # Consistent slug across plans
    description: str
    max_limit_per_month: int
    subscription_plan: DefaultSubscriptionPlan


@dataclass
class DefaultFeatureGroup:
    """
    Group of products, e.g. "Invoices"
    """

    name: str
    items: list[DefaultFeature]


@dataclass
class DefaultSubscriptionPlan:
    """
    This is a Stripe PRODUCT
    """

    name: str
    price_per_month: int
    description: str


# Default subscription plans
free_plan = DefaultSubscriptionPlan(
    name="Free Trial",
    price_per_month=0,
    description="Try out MyFinances",
)

starter_plan = DefaultSubscriptionPlan(
    name="Starter",
    price_per_month=5,
    description="For small businesses that need limited features",
)

growth_plan = DefaultSubscriptionPlan(
    name="Growth",
    price_per_month=10,
    description="For growing businesses that need a little extra",
)

# enterprise_plan = DefaultSubscriptionPlan(
#     name="Enterprise",
#     price_per_month=-1,
#     description="Additional customization for your ideal business",
# )

default_subscription_plans: list[DefaultSubscriptionPlan] = [free_plan, starter_plan, growth_plan]

# Default usage plans
default_usage_plans: list[DefaultFeatureGroup] = [
    DefaultFeatureGroup(
        "invoices",
        [
            # region "invoices-created"
            DefaultFeature(
                slug="invoices-created",
                description="Amount of invoices created per month",
                max_limit_per_month=10,
                subscription_plan=free_plan,
            ),
            DefaultFeature(
                slug="invoices-created",
                description="Amount of invoices created per month (starter plan)",
                max_limit_per_month=500,
                subscription_plan=starter_plan,
            ),
            DefaultFeature(
                slug="invoices-created",
                description="Amount of invoices created per month",
                max_limit_per_month=-1,
                subscription_plan=growth_plan,
            ),
            # endregion "invoices-created"
            # region "invoices-sent-via-schedule"
            DefaultFeature(
                slug="invoices-sent-via-schedule",
                description="Amount of invoices sent from a schedule per month",
                max_limit_per_month=1,
                subscription_plan=free_plan,
            ),
            DefaultFeature(
                slug="invoices-sent-via-schedule",
                description="Amount of invoices sent from a schedule per month",
                max_limit_per_month=50,
                subscription_plan=starter_plan,
            ),
            DefaultFeature(
                slug="invoices-sent-via-schedule",
                description="Amount of invoices sent from a schedule per month",
                max_limit_per_month=-1,
                subscription_plan=growth_plan,
            ),
            # endregion "invoices-sent-via-schedule"
        ],
    ),
    DefaultFeatureGroup(
        "teams",
        [
            # region "organization-access"
            DefaultFeature(
                slug="organization-access",
                description="Amount of invoices created per month (starter plan)",
                max_limit_per_month=1,
                subscription_plan=starter_plan,
            ),
            DefaultFeature(
                slug="organization-access",
                description="Amount of invoices created per month",
                max_limit_per_month=1,
                subscription_plan=growth_plan,
            ),
            # endregion "organization-access"
        ],
    ),
]
