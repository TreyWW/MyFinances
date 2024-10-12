from __future__ import annotations

from django.urls import path

from . import send, fetch, status

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
    path("fetch/", fetch.fetch_all_emails, name="fetch"),
    path("get_status/<str:status_id>/", status.get_status_view, name="get_status"),
    path("refresh_statuses/", status.refresh_all_statuses_view, name="refresh statuses"),
]

app_name = "emails"
