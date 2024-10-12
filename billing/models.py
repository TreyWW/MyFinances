from uuid import uuid4

from django.db import models

from backend.core.models import OwnerBase

from django.utils import timezone

from django.utils.timezone import now as timezone_now


class SubscriptionPlan(models.Model):
    """
    Subscription plans available for users.
    """

    name = models.CharField(max_length=50, unique=True)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)
    stripe_product_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_price_id = models.CharField(max_length=100, null=True, blank=True)


def __str__(self):
    return f"{self.name} - {self.price_per_month or 'free' if self.price_per_month != -1 else 'custom'}"


class UserSubscription(OwnerBase):
    """
    Track which subscription plan a user is currently subscribed to.
    """

    uuid = models.UUIDField(unique=True, default=uuid4)
    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    stripe_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    # Custom price only used for enterprise or negotiated plans
    custom_subscription_price_per_month = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.owner} - {self.subscription_plan.name} ({self.start_date} to {self.end_date or 'ongoing'})"

    @property
    def has_ended(self):
        return bool(self.end_date)

    @property
    def get_price(self):
        return self.custom_subscription_price_per_month or self.subscription_plan.price_per_month or "0.00"

    def end_now(self):
        self.end_date = timezone.now()
        self.save()
        return self


class PlanFeatureGroup(models.Model):
    name = models.CharField(max_length=50)  # E.g. 'invoices'


class PlanFeature(models.Model):
    """
    Details related to certain features. E.g. "emails sent", we can allow site admins to change prices, units, and customise their
    billing
    """

    slug = models.CharField(max_length=100)
    stripe_price_id = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(max_length=500, null=True, blank=True)

    max_limit_per_month = models.IntegerField(null=True, blank=True)

    subscription_plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="features")
    group = models.ForeignKey(PlanFeatureGroup, on_delete=models.CASCADE, related_name="features")

    def __str__(self):
        return f"{self.slug} - subscription id: {self.subscription_plan_id}"


class StripeWebhookEvent(models.Model):
    event_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=100)  # e.g. 'customer.subscription.created'
    data = models.JSONField()
    raw_event = models.JSONField()


class StripeCheckoutSession(OwnerBase):
    uuid = models.UUIDField(unique=True, default=uuid4)

    stripe_session_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE, related_name="checkout_sessions")
    features = models.ManyToManyField(PlanFeature, related_name="checkout_sessions")


class BillingUsage(OwnerBase):
    EVENT_TYPES = (
        ("usage", "Metered Usage"),
        # ("storage", "Storage"),
    )

    event_name = models.CharField(max_length=100)  # e.g. 'invoices-created'
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default="usage")
    quantity = models.PositiveSmallIntegerField(default=1)  # e.g. 1

    created_at = models.DateTimeField(auto_now_add=True)

    processed_at = models.DateTimeField(null=True, blank=True)
    processed = models.BooleanField(default=False)
    stripe_unique_usage_identifier = models.CharField(max_length=100, null=True, blank=True)

    def set_processed(self, processed_time):
        self.processed = True
        self.processed_at = processed_time or timezone_now()
        self.save()
        return self
