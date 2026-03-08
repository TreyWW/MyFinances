from typing import Type
import logging
from django.dispatch import receiver
from django.db.models.signals import post_save

from backend.clients.models import Client, DefaultValues

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Client)
def create_client_defaults(sender: Type[Client], instance: Client, created, **kwargs):
    if not created:
        return

    logger.info(f"Creating client defaults for client #{instance.id}")

    if instance.user:
        account_defaults, _ = DefaultValues.objects.get_or_create(user=instance.owner, client=None)
    else:
        account_defaults, _ = DefaultValues.objects.get_or_create(organization=instance.owner, client=None)

    defaults = DefaultValues.objects.create(client=instance, owner=instance.owner)  # type: ignore[misc]

    defaults.invoice_date_value = account_defaults.invoice_date_value
    defaults.invoice_date_type = account_defaults.invoice_date_type

    defaults.invoice_due_date_type = account_defaults.invoice_due_date_type
    defaults.invoice_due_date_value = account_defaults.invoice_due_date_value

    defaults.save(update_fields=["invoice_date_value", "invoice_date_type", "invoice_due_date_type", "invoice_due_date_value"])
