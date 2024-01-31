from django.urls import path

from . import fetch

urlpatterns = [
    path(
        "fetch/",
        fetch.fetch_all_receipts,
        name="fetch",
    ),
]

app_name = "receipts"
