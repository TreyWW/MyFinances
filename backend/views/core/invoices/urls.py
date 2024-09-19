from django.urls import path
from django.urls.conf import include

from . import save_bank_details
from .recurring.create import create_recurring_invoice_endpoint_handler
from .recurring.dashboard import invoices_recurring_dashboard_endpoint
from .recurring.edit import invoice_edit_page_endpoint
from .single import schedule, edit, create, view, manage_access
from .single.dashboard import invoices_single_dashboard_endpoint
from .single.overview import manage_invoice
from .recurring.overview import manage_recurring_invoice_profile_endpoint

SINGLE_INVOICE_URLS = [
    # path(
    #     "<int:invoice_id>/schedules/",
    #     schedule.view_schedules,
    #     name="schedules view",
    # ),
    path(
        "<int:invoice_id>/access/",
        manage_access.manage_access,
        name="manage_access",
    ),
    path(
        "<int:invoice_id>/access/create/",
        manage_access.create_code,
        name="manage_access create",
    ),
    path(
        "<str:code>/access/delete/",
        manage_access.delete_code,
        name="manage_access delete",
    ),
    path(
        "<int:invoice_id>/preview/",
        view.preview,
        name="preview",
    ),
    path(
        "<str:invoice_id>/edit/",
        edit.edit_invoice_page,
        # invoices.edit.invoice_edit_page_get,
        name="edit",
    ),
    path("", invoices_single_dashboard_endpoint, name="dashboard"),
    path(
        "create/",
        create.create_single_invoice_endpoint_handler,
        name="create",
    ),
    path(
        "<str:invoice_id>",
        manage_invoice,
        name="overview",
    ),
]

RECURRING_INVOICE_URLS = [
    path("", invoices_recurring_dashboard_endpoint, name="dashboard"),
    path(
        "create",
        create_recurring_invoice_endpoint_handler,
        name="create",
    ),
    path(
        "<str:invoice_profile_id>",
        manage_recurring_invoice_profile_endpoint,
        name="overview",
    ),
    path("<str:invoice_profile_id>/edit", invoice_edit_page_endpoint, name="edit"),
]

urlpatterns = [
    path("single/", include((SINGLE_INVOICE_URLS, "single"), namespace="single")),
    path("recurring/", include((RECURRING_INVOICE_URLS, "recurring"), namespace="recurring")),
    path("", invoices_single_dashboard_endpoint),
    path("save_bank_details/", save_bank_details.save_bank_details, name="save_bank_details"),
]

app_name = "invoices"
