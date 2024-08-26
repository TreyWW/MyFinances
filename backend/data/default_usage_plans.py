from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal


@dataclass
class Feature:
    slug: str
    description: str
    name: str
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
