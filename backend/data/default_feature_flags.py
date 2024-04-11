from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FeatureFlag:
    name: str
    description: str
    default: bool


default_feature_flags: list[FeatureFlag] = [
    FeatureFlag(name="areSignupsEnabled", description="Are new account creations allowed", default=True),
    FeatureFlag(
        name="isInvoiceSchedulingEnabled",
        description="Invoice Scheduling allows for clients to create invoice schedules that send and invoice at a specific date.",
        default=False,
    ),
    FeatureFlag(name="areUserEmailsAllowed", description="Are users allowed to send emails from YOUR DOMAIN to customers", default=False),
    FeatureFlag(
        name="areInvoiceRemindersEnabled",
        description="Invoice Reminders allow for clients to be reminded to pay an invoice.",
        default=False,
    ),
]
