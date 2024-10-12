from django.urls import path

from backend.core.webhooks.invoices.recurring import handle_recurring_invoice_webhook_endpoint

urlpatterns = [
    path("schedules/receive/recurring_invoices/", handle_recurring_invoice_webhook_endpoint, name="receive_recurring_invoices"),
]

app_name = "webhooks"
