from django.urls import path

from . import create, delete, edit, fetch

urlpatterns = [
    path(
        "create",
        create.create_invoice_endpoint,
        name="create",
    ),
    path(
        "delete/",
        delete.delete_invoice_endpoint,
        name="delete",
    ),
    path(
        "edit/",
        edit.edit_invoice_endpoint,
        name="edit",
    ),
    path("edit/<int:invoice_id>/set_status/<str:status>/", edit.change_status_endpoint, name="edit status"),
    path("edit/<str:invoice_id>/discount/", edit.edit_discount_endpoint, name="edit discount"),
    path("fetch/", fetch.fetch_all_invoices_endpoint, name="fetch"),
]

app_name = "invoices"
