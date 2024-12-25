from __future__ import annotations

from django.conf.urls import include
from django.urls import path, re_path

urlpatterns = [
    path("clients/", include("backend.api.public.endpoints.clients.urls")),
    path("invoices/", include("backend.api.public.endpoints.invoices.urls")),
]

app_name = "public"
