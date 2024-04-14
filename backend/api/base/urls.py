from django.urls import path
from . import modal, notifications

urlpatterns = [
    path(
        "modals/<str:modal_name>/retrieve",
        modal.open_modal,
        name="modal retrieve",
    ),
    path(
        "modals/<str:modal_name>/retrieve/<context_type>/<context_value>",
        modal.open_modal,
        name="modal retrieve with context",
    ),
    path(
        "modals/<str:modal_name>/<int:receipt_id>/",
        modal.edit_modal_receipts,
        name="modal edit context",
    ),
    path(
        "notifications/get",
        notifications.get_notification_html,
        name="notifications get",
    ),
    path(
        "notifications/delete/<int:id>",
        notifications.delete_notification,
        name="notifications delete",
    ),
]

app_name = "base"
