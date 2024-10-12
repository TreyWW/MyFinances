from datetime import timedelta
from typing import Type

from django.db import models
from django.db.models import QuerySet

from backend.models import TeamInvitation, InvoiceURL, PasswordSecret

from django.utils import timezone

"""
Every model MUST have the field "expires" as:

expires = models.DateTimeField(null=True, blank=True)
"""


def expire_and_cleanup_objects() -> str:
    deactivated_items: int = 0
    deleted_items: int = 0

    model_list: list[Type[models.Model]] = [TeamInvitation, InvoiceURL, PasswordSecret]

    now = timezone.now()

    for model in model_list:
        # Delete objects that have been inactive and expired for more than 14 days
        over_14_days_expired = model.all_objects.filter(expires__lte=now - timedelta(days=14))  # type: ignore[attr-defined]
        deleted_items += over_14_days_expired.count()
        over_14_days_expired.delete()

        # Deactivate expired items that got missed
        to_deactivate: QuerySet[models.Model] = model.all_objects.filter(expires__lte=now, active=True)  # type: ignore[attr-defined]

        deactivated_items += to_deactivate.count()
        to_deactivate.update(active=False)

    return f"Deactivated {deactivated_items} objects and deleted {deleted_items} objects."
