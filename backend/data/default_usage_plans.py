from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass
class Feature:
    slug: str
    description: str
    name: str
    subscription_plan: SubscriptionPlanItem
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
class SubscriptionPlanItem:
    name: str
    price_per_month: Decimal
    description: str
    maximum_duration_months: int


free_plan = SubscriptionPlanItem(
    name="free trial",
    price_per_month=Decimal(0.00),
    description="Try out MyFinances",
    maximum_duration_months=1,
)

starter_plan = SubscriptionPlanItem(
    name="starter",
    price_per_month=Decimal(5),
    description="For small businesses that need limited features",
    maximum_duration_months=0,
)

growth_plan = SubscriptionPlanItem(
    name="growth",
    price_per_month=Decimal(10),
    description="For growing businesses that need a little extra",
    maximum_duration_months=0,
)

enterprise_plan = SubscriptionPlanItem(
    name="enterprise",
    price_per_month=Decimal(-1),
    description="Additional customisation for your ideal business",
    maximum_duration_months=0,
)

default_subscription_plans: list[SubscriptionPlanItem] = [free_plan, starter_plan, growth_plan, enterprise_plan]

default_usage_plans: list[FeatureGroup] = [
    FeatureGroup(
        "invoices",
        [
            # region invoices-created-free-plan
            Feature(
                slug="invoices-created-free-plan",
                name="Invoices Created (free plan)",
                description="Amount of invoices created per month",
                free_tier_limit=10,
                free_period_in_months=1,
                unit="invocations",
                cost_per_unit=Decimal(0.05),
                units_per_cost=1,
                minimum_billable_size=1,
                subscription_plan=free_plan,
            ),
            # endregion
            # region invoices-created-starter-plan
            Feature(
                slug="invoices-created-starter-plan",
                name="Invoices Created (starter plan)",
                description="Amount of invoices created per month",
                free_tier_limit=100,
                free_period_in_months=3,
                unit="invocations",
                cost_per_unit=Decimal(0.50),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=starter_plan,
            ),
            # endregion
            # region invoices-created-growth-plan
            Feature(
                slug="invoices-created-growth-plan",
                name="Invoices Created (growth plan)",
                description="Amount of invoices created per month",
                free_tier_limit=300,
                free_period_in_months=12,
                unit="invocations",
                cost_per_unit=Decimal(0.10),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=growth_plan,
            ),
            # endregion
            # region invoices-sent-via-schedule-free-plan
            Feature(
                slug="invoices-sent-via-schedule-free-plan",
                name="Invoices Sent from Schedule (free plan)",
                description="Amount of invoices sent from a schedule per month",
                free_tier_limit=1,
                free_period_in_months=1,
                unit="invoice(s)",
                cost_per_unit=Decimal(0.01),
                units_per_cost=1,
                minimum_billable_size=1,
                subscription_plan=free_plan,
            ),
            # endregion
            # region invoices-sent-via-schedule-starter-plan
            Feature(
                slug="invoices-sent-via-schedule-starter-plan",
                name="Invoices Sent from schedule (starter plan)",
                description="Amount of invoices sent from a schedule per month",
                free_tier_limit=10,
                free_period_in_months=3,
                unit="invoice(s)",
                cost_per_unit=Decimal(1.00),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=starter_plan,
            ),
            # endregion
            # region invoices-sent-via-schedule-growth-plan
            Feature(
                slug="invoices-sent-via-schedule-growth-plan",
                name="Invoices Sent from schedule (growth plan)",
                description="Amount of invoices sent from a schedule per month",
                free_tier_limit=75,
                free_period_in_months=12,
                unit="invoice(s)",
                cost_per_unit=Decimal(1.00),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=growth_plan,
            ),
            # endregion
        ],
    ),
]
