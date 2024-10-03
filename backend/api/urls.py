from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("base/", include("backend.api.base.urls")),
    path("teams/", include("backend.api.teams.urls")),
    path("receipts/", include("backend.api.receipts.urls")),
    path("invoices/", include("backend.api.invoices.urls")),
    path("clients/", include("backend.api.clients.urls")),
    path("settings/", include("backend.api.settings.urls")),
    path("file_storage/", include("backend.api.file_storage.urls")),
    path("products/", include("backend.api.products.urls")),
    path("quotas/", include("backend.api.quotas.urls")),
    path("emails/", include("backend.api.emails.urls")),
    path("reports/", include("backend.api.reports.urls")),
    path("maintenance/", include("backend.api.maintenance.urls")),
    path("landing_page/", include("backend.api.landing_page.urls")),
    path("public/", include("backend.api.public.urls")),
]

app_name = "api"
