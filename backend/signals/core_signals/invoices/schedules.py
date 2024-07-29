from typing import Type
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save

from backend.service.boto3.scheduler.create_schedule import update_boto_schedule

from backend.models import InvoiceRecurringSet

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceRecurringSet)
def create_client_defaults(sender: Type[InvoiceRecurringSet], instance: InvoiceRecurringSet, created, **kwargs):
    if not created:
        return

    update_boto_schedule.delay(instance.pk)
