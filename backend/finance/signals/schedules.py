from typing import Type
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save

from backend.core.service.boto3.scheduler.create_schedule import create_boto_schedule
from backend.core.service.boto3.scheduler.update_schedule import update_boto_schedule

from backend.finance.models import InvoiceRecurringProfile

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceRecurringProfile)
def create_recurring_schedule(
    sender: Type[InvoiceRecurringProfile], instance: InvoiceRecurringProfile, created, raw, using, update_fields, **kwargs
):
    if not created:
        if not instance.active:
            print("Schedule isn't active, don't update.")
            return None
        print("Schedule updated calling update_boto_schedule")
        return update_boto_schedule(instance.pk)

    logger.info(f"Invoice recurring profile was just created")

    create_boto_schedule(instance)
