from django.db.models.signals import post_save
from django.dispatch import receiver
from billing.models import StripeWebhookEvent
from billing.service.checkout_completed import checkout_completed
from billing.service.subscription_ended import subscription_ended
from billing.service.entitlements import entitlements_updated_via_stripe_webhook


@receiver(post_save, sender=StripeWebhookEvent)
def stripe_webhook_event_created(sender, instance: StripeWebhookEvent, **kwargs):
    match instance.event_type:
        case "checkout.session.completed":
            checkout_completed(instance)
        case "customer.subscription.deleted":
            subscription_ended(instance)
        case "entitlements.active_entitlement_summary.updated":
            entitlements_updated_via_stripe_webhook(instance)
        case _:
            print(f"Unhandled event type: {instance.event_type}")
