from django.urls import path
from .webhook_task_queue_handler import webhook_task_queue_handler_view_endpoint

urlpatterns = [
    path(
        "receive/global/",
        webhook_task_queue_handler_view_endpoint,
        name="receive_global",
    )
]

app_name = "webhooks"
