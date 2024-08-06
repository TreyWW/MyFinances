from django.urls import path, include

from . import fetch, delete, edit, schedule, manage
from .create import set_destination
from .create.services import add_service
from .recurring.delete import delete_invoice_recurring_set_endpoint
from .recurring.edit import edit_invoice_recurring_set_endpoint
from .recurring.fetch import fetch_all_recurring_invoices_endpoint
from .recurring.generate_next_invoice_now import generate_next_invoice_now_endpoint
from .recurring.poll import poll_recurring_schedule_update_endpoint
from .recurring.update_status import recurring_set_change_status_endpoint

SINGLE_INVOICE_URLS = [
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

RECURRING_INVOICE_URLS = [
    path("fetch/", fetch_all_recurring_invoices_endpoint, name="fetch"),
    path("edit/<int:invoice_set_id>/set_status/<str:status>/", recurring_set_change_status_endpoint, name="edit status"),
    path("poll/<str:invoice_set_id>/update_schedule/", poll_recurring_schedule_update_endpoint, name="poll_update_schedule"),
    path("<str:invoice_set_id>/generate_next_invoice/", generate_next_invoice_now_endpoint, name="generate next invoice"),
    path("<str:invoice_set_id>/edit/", edit_invoice_recurring_set_endpoint, name="edit"),
    path("delete/", delete_invoice_recurring_set_endpoint, name="delete"),
]

CREATE_INVOICE_URLS = [
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
]

urlpatterns = [
    path("single/", include((SINGLE_INVOICE_URLS, "single"), namespace="single")),
    path("recurring/", include((RECURRING_INVOICE_URLS, "recurring"), namespace="recurring")),
    path("create/", include((CREATE_INVOICE_URLS, "create"), namespace="create")),
]

app_name = "invoices"
