from __future__ import annotations

from django.urls import path

from . import send

urlpatterns = [
    path(
        "send/single/",
        send.send_single_email_view,
        name="send single",
    ),
    path(
        "send/bulk/",
        send.send_bulk_email_view,
        name="send bulk",
    ),
]

app_name = "emails"
