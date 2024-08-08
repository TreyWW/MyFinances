from typing import Type
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save

from backend.service.boto3.scheduler.create_schedule import update_boto_schedule

from backend.models import InvoiceRecurringSet

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceRecurringSet)
def create_recurring_schedule(sender: Type[InvoiceRecurringSet], instance: InvoiceRecurringSet, created, **kwargs):
    if not created:
        return

    logger.info(f"Invoice recurring set was just created")

    update_boto_schedule(instance.pk)
