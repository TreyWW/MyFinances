from __future__ import annotations

from django.urls import include
from django.urls import path

urlpatterns = [
    path("finance/", include("backend.finance.api.urls")),
]

app_name = "api"
