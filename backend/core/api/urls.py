from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("base/", include("backend.core.api.base.urls")),
    path("teams/", include("backend.core.api.teams.urls")),
    path("settings/", include("backend.core.api.settings.urls")),
    path("quotas/", include("backend.core.api.quotas.urls")),
    path("clients/", include("backend.clients.api.urls")),
    path("emails/", include("backend.core.api.emails.urls")),
    path("maintenance/", include("backend.core.api.maintenance.urls")),
    path("landing_page/", include("backend.core.api.landing_page.urls")),
    path("public/", include("backend.core.api.public.urls")),
    path("", include("backend.finance.api.urls")),
]

app_name = "api"
