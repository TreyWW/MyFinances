from django.urls import path

from . import download, access

urlpatterns = [
    # path(
    #     "download/<str:invoice_uuid>/",
    #     download.download_invoice,
    #     name="download"
    # ), # This doesnt parse the HTML properly; need to fix when remaking invoice.
    path("create_access_code/<int:invoice_id>/", access.create_code, name="create_code"),
]

app_name = "invoices"
