from django.urls import path
from django.urls.conf import include

from backend.finance.views.invoices.recurring.create import create_recurring_invoice_endpoint_handler
from backend.finance.views.invoices.recurring.dashboard import invoices_recurring_dashboard_endpoint
from backend.finance.views.invoices.recurring.edit import invoice_edit_page_endpoint
from backend.finance.views.invoices.single.create import create_single_invoice_endpoint_handler
from backend.finance.views.invoices.single.dashboard import invoices_single_dashboard_endpoint
from backend.finance.views.invoices.recurring.overview import manage_recurring_invoice_profile_endpoint
from backend.finance.views.invoices.single.edit import edit_invoice_page
from backend.finance.views.invoices.single import manage_access
from backend.finance.views.invoices.single.overview import manage_invoice
from backend.finance.views.invoices.single.view import preview

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
        preview,
        name="preview",
    ),
    path(
        "<str:invoice_id>/edit/",
        edit_invoice_page,
        # invoices.edit.invoice_edit_page_get,
        name="edit",
    ),
    path("", invoices_single_dashboard_endpoint, name="dashboard"),
    path(
        "create/",
        create_single_invoice_endpoint_handler,
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
]

app_name = "invoices"
