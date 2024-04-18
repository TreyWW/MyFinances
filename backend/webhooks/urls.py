from django.urls import path, include

from backend.webhooks.invoices.schedules import receive_scheduled_invoice_schedule, receive_scheduled_invoice_reminder

urlpatterns = [
    path("schedules/receive/schedule/", receive_scheduled_invoice_schedule, name="receive_scheduled_invoice schedule"),
    path("schedules/receive/reminder/", receive_scheduled_invoice_reminder, name="receive_scheduled_invoice reminder"),
]

app_name = "webhooks"
