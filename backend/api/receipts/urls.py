from django.urls import path
from . import delete, new, fetch, download, edit

urlpatterns = [
    path(
        "delete/<int:id>/",
        delete.receipt_delete,
        name="delete",
    ),
    path(
        "new/",
        new.receipt_create,
        name="new",
    ),
    path(
        "edit/<int:receipt_id>/",
        edit.edit_receipt,
        name="edit",
    ),
    path(
        "fetch/",
        fetch.fetch_all_receipts,
        name="fetch",
    ),
    path(
        "download/<int:receipt_id>/",
        download.generate_download_link,
        name="generate_download_link",
    ),
    path("cdn/<uuid:token>/", download.download_receipt, name="download_receipt"),
]

app_name = "receipts"
