from __future__ import annotations

from django.conf.urls import include
from django.urls import path, re_path
from rest_framework.authentication import TokenAuthentication

from .endpoints.system_health import system_health_endpoint

INTERNAL_URLS = [path("health/", system_health_endpoint, name="public-system-health")]

urlpatterns = [
    path("internal/", include(INTERNAL_URLS)),
    path("clients/", include("backend.core.api.public.endpoints.clients.urls")),
    path("invoices/", include("backend.core.api.public.endpoints.Invoices.urls")),
    path("webhooks/", include("backend.core.api.public.endpoints.webhooks.urls")),
]

app_name = "public"
