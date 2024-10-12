import logging
from datetime import datetime

import stripe
from django.db.models.signals import post_save
from django.dispatch import receiver

from backend.finance.models import Invoice
from backend.core.models import User
from billing.models import BillingUsage

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BillingUsage)
def usage_occurred(sender, instance: BillingUsage, created, **kwargs):
    if not created or instance.processed:
        return

    if instance.event_type != "usage":
        return  # may add storage at a later point

    if not instance.owner:
        print("CANNOT HANDLE ORGS AT THE MOMENT!")
        return  # todo: cannot handle organisations at the moment

    stripe_customer_id = instance.owner.stripe_customer_id

    if not stripe_customer_id:
        print(f"No stripe customer id for actor #{'usr_' if isinstance(instance.owner, User) else 'org_'}{instance.owner.id}")
        return  # todo

    meter_event = stripe.billing.MeterEvent.create(
        event_name=instance.event_name, payload={"value": str(instance.quantity), f"stripe_customer_id": stripe_customer_id}
    )

    if meter_event.created:
        instance.stripe_unique_usage_identifier = meter_event.identifier
        instance.set_processed(datetime.fromtimestamp(meter_event.created))

    return


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
