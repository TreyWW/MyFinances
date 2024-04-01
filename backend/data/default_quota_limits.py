from dataclasses import dataclass
from typing import List, Literal


@dataclass
class QuotaItem:
    slug: str
    name: str
    description: str
    default_value: int
    adjustable: bool
    period: Literal["forever", "per_month", "per_day", "per_client", "per_invoice", "per_team", "per_quota"]


@dataclass
class QuotaGroup:
    name: str
    items: List[QuotaItem]


default_quota_limits: List[QuotaGroup] = [
    QuotaGroup(
        "invoices",
        [
            QuotaItem(
                slug="count",
                name="Creations per month",
                description="Amount of invoices created per month",
                default_value=100,
                period="per_month",
                adjustable=True,
            ),
            QuotaItem(
                slug="schedules",
                name="Schedules per month",
                description="Amount of invoice scheduled sends allowed per month",
                default_value=100,
                period="per_month",
                adjustable=True,
            ),
            QuotaItem(
                slug="access_codes",
                name="Created access codes",
                description="Amount of invoice access codes allowed per invoice",
                default_value=3,
                period="per_invoice",
                adjustable=True,
            ),
        ],
    ),
    QuotaGroup(
        "receipts",
        [
            QuotaItem(
                slug="count",
                name="Created receipts",
                description="Amount of receipts stored per month",
                default_value=100,
                period="per_month",
                adjustable=True,
            )
        ],
    ),
    QuotaGroup(
        "clients",
        [
            QuotaItem(
                slug="count",
                name="Created clients",
                description="Amount of clients stored in total",
                default_value=40,
                period="forever",
                adjustable=True,
            )
        ],
    ),
    QuotaGroup(
        "teams",
        [
            QuotaItem(
                slug="count",
                name="Created teams",
                description="Amount of teams created in total",
                default_value=3,
                period="forever",
                adjustable=True,
            ),
            QuotaItem(
                slug="joined",
                name="Joined teams",
                description="Amount of teams that you have joined in total",
                default_value=5,
                period="forever",
                adjustable=True,
            ),
            QuotaItem(
                slug="user_count",
                name="Users per team",
                description="Amount of users per team",
                default_value=10,
                period="per_team",
                adjustable=True,
            ),
        ],
    ),
    QuotaGroup(
        "quota_increase",
        [
            QuotaItem(
                slug="request",
                name="Quota Increase Request",
                description="Amount of increase requests allowed per quota",
                default_value=1,
                period="per_quota",
                adjustable=False,
            ),
            QuotaItem(
                slug="requests_per_month_per_quota",
                name="Quota Increase Requests per month",
                description="Amount of increase requests allowed per month per quota",
                period="per_quota",
                default_value=1,
                adjustable=False,
            ),
        ],
    ),
]
