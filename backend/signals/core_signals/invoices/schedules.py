from typing import Type
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save

from backend.celery_tasks.recurring_invoices.on_create import create_boto_schedule

from uuid import uuid4
from backend.models import InvoiceRecurringSet

logger = logging.getLogger(__name__)


@receiver(post_save, sender=InvoiceRecurringSet)
def create_client_defaults(sender: Type[InvoiceRecurringSet], instance: InvoiceRecurringSet, created, **kwargs):
    if not created:
        create_boto_schedule.delay(instance.pk)
