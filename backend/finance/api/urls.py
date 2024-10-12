from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("receipts/", include("backend.finance.api.receipts.urls")),
    path("invoices/", include("backend.finance.api.invoices.urls")),
    path("products/", include("backend.finance.api.products.urls")),
    path("reports/", include("backend.finance.api.reports.urls")),
]

app_name = "finance"
