from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass
class Feature:
    slug: str  # Consistent slug across plans
    name: str
    description: str
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


# Default subscription plans
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
    description="Additional customization for your ideal business",
    maximum_duration_months=0,
)

default_subscription_plans: list[SubscriptionPlanItem] = [free_plan, starter_plan, growth_plan, enterprise_plan]

# Default usage plans
default_usage_plans: list[FeatureGroup] = [
    FeatureGroup(
        "invoices",
        [
            # region "invoices-created"
            Feature(
                slug="invoices-created",
                name="Invoices Created (free plan)",
                description="Amount of invoices created per month",
                free_tier_limit=10,
                free_period_in_months=1,
                unit="invocations",
                cost_per_unit=Decimal(1),
                units_per_cost=0,
                minimum_billable_size=1,
                subscription_plan=free_plan,
            ),
            Feature(
                slug="invoices-created",
                name="Invoices Created",
                description="Amount of invoices created per month (starter plan)",
                free_tier_limit=100,
                free_period_in_months=3,
                unit="invocations",
                cost_per_unit=Decimal(1),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=starter_plan,
            ),
            Feature(
                slug="invoices-created",
                name="Invoices Created (growth plan)",
                description="Amount of invoices created per month",
                free_tier_limit=300,
                free_period_in_months=12,
                unit="invocations",
                cost_per_unit=Decimal(0.90),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=growth_plan,
            ),
            # endregion "invoices-created"
            # region "invoices-sent-via-schedule"
            Feature(
                slug="invoices-sent-via-schedule",
                name="Invoices Sent from Schedule (free plan)",
                description="Amount of invoices sent from a schedule per month",
                free_tier_limit=1,
                free_period_in_months=1,
                unit="invoice(s)",
                cost_per_unit=Decimal(0.10),
                units_per_cost=1,
                minimum_billable_size=1,
                subscription_plan=free_plan,
            ),
            Feature(
                slug="invoices-sent-via-schedule",
                name="Invoices Sent from Schedule (starter plan)",
                description="Amount of invoices sent from a schedule per month",
                free_tier_limit=10,
                free_period_in_months=3,
                unit="invoice(s)",
                cost_per_unit=Decimal(0.10),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=starter_plan,
            ),
            Feature(
                slug="invoices-sent-via-schedule",
                name="Invoices Sent from Schedule (growth plan)",
                description="Amount of invoices sent from a schedule per month",
                free_tier_limit=75,
                free_period_in_months=12,
                unit="invoice(s)",
                cost_per_unit=Decimal(0.10),
                units_per_cost=1000,
                minimum_billable_size=1,
                subscription_plan=growth_plan,
            ),
            # endregion "invoices-sent-via-schedule"
        ],
    ),
    FeatureGroup(
        "teams",
        [
            # region "organization-access"
            # Feature(
            #     slug="organization-access",
            #     name="Organization Access ()",
            #     description="Amount of invoices created per month",
            #     free_tier_limit=10,
            #     free_period_in_months=1,
            #     unit="invocations",
            #     cost_per_unit=Decimal(1),
            #     units_per_cost=0,
            #     minimum_billable_size=1,
            #     subscription_plan=free_plan,
            # ),
            Feature(
                slug="organization-access",
                name="Organization Access ()",
                description="Amount of invoices created per month (starter plan)",
                free_tier_limit=0,
                free_period_in_months=0,
                unit="team access (unlimited /pm)",
                cost_per_unit=Decimal(3),
                units_per_cost=1,
                minimum_billable_size=1,
                subscription_plan=starter_plan,
            ),
            Feature(
                slug="organization-access",
                name="Organization Access ()",
                description="Amount of invoices created per month",
                free_tier_limit=0,
                free_period_in_months=0,
                unit="team access (unlimited /pm)",
                cost_per_unit=Decimal(3),
                units_per_cost=1,
                minimum_billable_size=1,
                subscription_plan=growth_plan,
            ),
            # endregion "organization-access"
        ],
    ),
    FeatureGroup(
        "Data Transfer",
        [
            Feature(
                slug="data-transfer",
                name="Data Transfer",
                description="Amount of data transferred per month",
                free_tier_limit=5,
                free_period_in_months=-1,
                unit="GB",
                cost_per_unit=Decimal("0.10"),
                units_per_cost=1,  # Cost applies to each full GB
                minimum_billable_size=0.125,  # Minimum billable size is 128 (not raw MB)
                subscription_plan=starter_plan,
            )
        ],
    ),
    FeatureGroup(
        "File Storage",
        [
            Feature(
                slug="storage",
                name="Storage",
                description="Storage usage charged per GB per month",
                free_tier_limit=10,  # Free 10 GB per month
                free_period_in_months=-1,  # Infinite (always 10 GB/pm free)
                unit="GB",
                cost_per_unit=Decimal("0.02"),  # Cost per GB per month
                units_per_cost=1,  # Cost applies to 1 GB
                minimum_billable_size=0.125,  # Minimum 128 MB (not raw MB)
                subscription_plan=starter_plan,
            )
        ],
    ),
]
