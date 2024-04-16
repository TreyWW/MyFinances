from django.urls import path, include

from backend.api.invoices.schedule import receive_scheduled_invoice

urlpatterns = [
    path("schedules/receive/", receive_scheduled_invoice, name="receive_scheduled_invoice"),
]

app_name = "webhooks"
