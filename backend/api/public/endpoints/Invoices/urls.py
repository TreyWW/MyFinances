from django.urls import path

from . import create, list, get, download_pdf

urlpatterns = [
    path(
        "create",
        create.create_invoice_endpoint,
        name="create",
    ),
    # path(
    #     "delete/",
    #     delete.delete_invoice_endpoint,
    #     name="delete",
    # ),
    # path(
    #     "edit/",
    #     edit.edit_invoice_endpoint,
    #     name="edit",
    # ),
    # path(
    #     "edit/<int:invoice_id>/set_status/<str:status>/",
    #     edit.change_status_endpoint,
    #     name="edit status"
    # ),
    # path(
    #     "edit/<str:invoice_id>/discount/",
    #     edit.edit_discount_endpoint,
    #     name="edit discount"
    # ),
    path("", list.list_invoices_endpoint, name="list"),
    path("<str:id>/", get.get_invoices_endpoint, name="get"),
    path("<str:id>/download/", download_pdf.download, name="download"),
]

app_name = "invoices"
