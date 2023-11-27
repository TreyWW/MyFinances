from django.urls import path
from . import delete, new, fetch

urlpatterns = [
    path(
        "delete/<int:id>",
        delete.receipt_delete,
        name="delete",
    ),
    path(
        "new",
        new.receipt_create,
        name="new",
    ),
    path(
        "fetch",
        fetch.fetch_receipts,
        name="fetch",
    ),
]

app_name = "receipts"
