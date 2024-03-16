from django.urls import path

from . import schedule, edit, dashboard, create, manage_access, view

invoice_urls = [
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
]

urlpatterns = invoice_urls + [
    path(
        "",
        dashboard.invoices_dashboard,
        name="dashboard",
    ),
    path(
        "create/",
        create.create_invoice_page,
        name="create",
    ),
]

app_name = "invoices"
