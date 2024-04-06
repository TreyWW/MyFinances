from __future__ import annotations

from django.urls import path

from . import send

urlpatterns = [
    path(
        "send/",
        send.send_email_view,
        name="dashboard",
    ),
]

app_name = "emails"
