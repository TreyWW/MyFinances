from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("base/", include("backend.api.base.urls")),
    path("admin/", include("backend.api.admin.urls")),
    path("teams/", include("backend.api.teams.urls")),
    path("receipts/", include("backend.api.receipts.urls")),
    path("invoices/", include("backend.api.invoices.urls")),
    path("clients/", include("backend.api.clients.urls")),
    path("settings/", include("backend.api.settings.urls")),
    path("products/", include("backend.api.products.urls")),
    path("currency_converter/", include("backend.api.currency_converter.urls")),
    path("quotas/", include("backend.api.quotas.urls")),
    path("emails/", include("backend.api.emails.urls")),
    path("hc/", include("backend.api.healthcheck.urls")),
]

app_name = "api"
