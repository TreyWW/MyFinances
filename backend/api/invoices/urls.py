from django.urls import path

from . import fetch, delete, edit, schedule, manage, reminders
from .create import set_destination
from .create.services import add

urlpatterns = [
    path(
        "add_service/",
        add.add_service,
        name="services add",
    ),
    path(
        "set_destination/to/",
        set_destination.set_destination_to,
        name="set_destination to",
    ),
    path(
        "set_destination/from/",
        set_destination.set_destination_from,
        name="set_destination from",
    ),
    path(
        "delete/",
        delete.delete_invoice,
        name="delete",
    ),
    path(
        "edit/",
        edit.edit_invoice,
        name="edit",
    ),
    path("edit/<int:invoice_id>/set_status/<str:status>/", edit.change_status, name="edit status"),
    path("fetch/", fetch.fetch_all_invoices, name="fetch"),
    path("schedules/receive/", schedule.receive_scheduled_invoice, name="receive_scheduled_invoice"),
    path("create_schedule/", schedule.create_schedule, name="create_schedule"),
    path("schedules/onetime/<str:schedule_id>/cancel/", schedule.cancel_onetime_schedule, name="schedules onetime cancel"),
    path("schedules/onetime/fetch/<str:invoice_id>/", schedule.fetch_onetime_schedules, name="schedules onetime fetch"),
    path("reminders/fetch/<str:invoice_id>", reminders.fetch_reminders, name="reminders fetch"),
    path("manage/<int:invoice_id>/tabs/preview/", manage.tab_preview_invoice, name="tab preview"),
]

app_name = "invoices"
