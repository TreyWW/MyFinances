from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("clients/", include("backend.clients.api.urls", namespace="clients")),
    path("finance/", include("backend.finance.api.urls", namespace="finance")),
]

app_name = "api"
