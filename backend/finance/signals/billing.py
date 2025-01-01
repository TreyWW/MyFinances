from billing.models import BillingUsage
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.models import Invoice


@receiver(post_save, sender=Invoice)
def created_invoice(sender, instance: Invoice, created, **kwargs):
    if not created:
        return

    BillingUsage.objects.create(
        owner=instance.owner,
        event_name="invoices_created",
    )

    if instance.invoice_recurring_profile:
        BillingUsage.objects.create(
            owner=instance.owner,
            event_name="invoice_schedule_invocations",
        )
    return
