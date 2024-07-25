from django.urls import path
from django.urls.conf import include

from .dashboard import invoices_dashboard_core_endpoint
from .recurring.dashboard import invoices_recurring_dashboard_endpoint
from .single import schedule, edit, create, view, manage_access
from .single.dashboard import invoices_single_dashboard_endpoint

SINGLE_INVOICE_URLS = [
    path(
        "<int:invoice_id>/schedules/",
        schedule.view_schedules,
        name="schedules view",
    ),
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
]

RECURRING_INVOICE_URLS = [
    path("", invoices_recurring_dashboard_endpoint, name="dashboard"),
]

urlpatterns = [
    path("single/", include((SINGLE_INVOICE_URLS, "single"), namespace="single")),
    path("recurring/", include((RECURRING_INVOICE_URLS, "recurring"), namespace="recurring")),
    path("", invoices_single_dashboard_endpoint),
    path(
        "create/",
        create.create_invoice_page,
        name="create",
    ),
    path("dashboard/temp", invoices_dashboard_core_endpoint, name="dashboard core"),
]

app_name = "invoices"
