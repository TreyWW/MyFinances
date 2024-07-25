from django.urls import path, include

from . import fetch, delete, edit, schedule, manage
from .create import set_destination
from .create.services import add_service

SINGLE_INVOICE_URLS = [
    path(
        "add_service/",
        add_service.add_service_endpoint,
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
    path("edit/<str:invoice_id>/discount/", edit.edit_discount, name="edit discount"),
    path("fetch/", fetch.fetch_all_invoices, name="fetch"),
    path("create_schedule/", schedule.create_schedule, name="create_schedule"),
    path("schedules/onetime/<str:schedule_id>/cancel/", schedule.cancel_onetime_schedule, name="schedules onetime cancel"),
    path("schedules/onetime/fetch/<str:invoice_id>/", schedule.fetch_onetime_schedules, name="schedules onetime fetch"),
    path("", include("backend.api.invoices.reminders.urls")),
]

RECURRING_INVOICE_URLS = []

urlpatterns = [
    path("single/", include((SINGLE_INVOICE_URLS, "single"), namespace="single")),
    path("recurring/", include((SINGLE_INVOICE_URLS, "recurring"), namespace="recurring")),
]

app_name = "invoices"
