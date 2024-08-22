from django.urls import path
from . import modal, notifications, breadcrumbs

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
        "notifications/get",
        notifications.get_notification_html,
        name="notifications get",
    ),
    path("notifications/get_count", notifications.get_notification_count_html, name="notifications get count"),
    path(
        "notifications/delete/<int:id>",
        notifications.delete_notification,
        name="notifications delete",
    ),
    path("breadcrumbs/refetch/", breadcrumbs.update_breadcrumbs_endpoint, name="breadcrumbs refetch"),
]

app_name = "base"
