from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from django.db import models
from backend.core.data.default_email_templates import (
    recurring_invoices_invoice_created_default_email_template,
    recurring_invoices_invoice_overdue_default_email_template,
    recurring_invoices_invoice_cancelled_default_email_template,
)
from backend.core.models import OwnerBase, User, UserSettings, _private_storage


class WebhookSubscription(OwnerBase):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    active = models.BooleanField(default=True)
    url = models.URLField(max_length=200)
    description = models.CharField(max_length=100, null=True, blank=True)
    event_types = models.JSONField(default=list)
    secret_key = models.CharField(max_length=100, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)


class WebhookEventLog(OwnerBase):
    class Status(models.TextChoices):
        PENDING = "pending"
        SUCCESS = "success"
        FAILED = "failed"

    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    subscription = models.ForeignKey(WebhookSubscription, on_delete=models.CASCADE, related_name="logs")
    event_type = models.CharField(max_length=100)
    description = models.CharField(max_length=100, null=True, blank=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)


class WebhookDeliverySendLog(OwnerBase):
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    response_body = models.JSONField()
    response_status_code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
