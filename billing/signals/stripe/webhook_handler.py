from django.db.models.signals import post_save
from django.dispatch import receiver

from billing.models import StripeWebhookEvent
from billing.service.checkout_completed import checkout_completed
from billing.service.subscription_ended import subscription_ended


@receiver(post_save, sender=StripeWebhookEvent)
def stripe_webhook_event_created(sender, instance: StripeWebhookEvent, **kwargs):
    match instance.event_type:
        # case ("price.created", ""):
        #     ...
        case "checkout.session.completed":
            return checkout_completed(instance)
        case "customer.subscription.deleted":
            return subscription_ended(instance)
        case _:
            ...
