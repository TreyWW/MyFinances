from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass
class Feature:
    slug: str
    description: str
    name: str
    subscription_plan: SubscriptionPlan
    free_tier_limit: float
    free_period_in_months: int
    unit: str
    cost_per_unit: Decimal
    units_per_cost: float
    minimum_billable_size: float


@dataclass
class FeatureGroup:
    name: str
    items: list[Feature]


@dataclass
class SubscriptionPlan:
    name: str
    price_per_month: Decimal
    description: str
    maximum_duration_months: int


default_subscription_plans: list[SubscriptionPlan] = [
    SubscriptionPlan(
        name="free trial",
        price_per_month=Decimal(0.00),
        description="Try out MyFinances",
        maximum_duration_months=1,
    ),
    SubscriptionPlan(
        name="starter",
        price_per_month=Decimal(5),
        description="For small businesses that need limited features",
        maximum_duration_months=0,
    ),
    SubscriptionPlan(
        name="growth",
        price_per_month=Decimal(10),
        description="For growing businesses that need a little extra",
        maximum_duration_months=0,
    ),
    SubscriptionPlan(
        name="enterprise",
        price_per_month=Decimal(-1),
        description="For additional customisation for your ideal business",
        maximum_duration_months=0,
    ),
]

default_usage_plans: list[FeatureGroup] = [
    FeatureGroup(
        "invoices",
        [
            Feature(
                slug="invoices-created",
                name="Invoices Created",
                description="Amount of invoices created per month",
                free_tier_limit=100,
                free_period_in_months=3,
                unit="invocations",
                cost_per_unit=Decimal(2.00),
                units_per_cost=1000,
                minimum_billable_size=1,
            ),
        ],
    ),
]

default
