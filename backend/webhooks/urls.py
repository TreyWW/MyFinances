from django.urls import path, include

from backend.webhooks.invoices.recurring import handle_recurring_invoice_webhook_endpoint
from backend.webhooks.webhook_task_queue_handler import webhook_task_queue_handler_view_endpoint

# from backend.webhooks.invoices.schedules import receive_scheduled_invoice_schedule, receive_scheduled_invoice_reminder

urlpatterns = [
    # path("schedules/receive/schedule/", receive_scheduled_invoice_schedule, name="receive_scheduled_invoice schedule"),
    # path("schedules/receive/reminder/", receive_scheduled_invoice_reminder, name="receive_scheduled_invoice reminder"),
    path("schedules/receive/recurring_invoices/", handle_recurring_invoice_webhook_endpoint, name="receive_recurring_invoices"),
    path("receive/global/", webhook_task_queue_handler_view_endpoint, name="receive_global"),
]

app_name = "webhooks"
