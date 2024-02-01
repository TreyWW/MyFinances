from django.urls import path

from . import fetch, download

urlpatterns = [
    path(
        "fetch/",
        fetch.fetch_all_receipts,
        name="fetch",
    ),
    path(
        "download/<str:token>/",
        download.download_receipt,
        name="download"
    ),
    path(
      "get_download_token/<int:receipt_id>/",
      download.get_download_token,
      name="get_download_token"
    )
]

app_name = "receipts"
