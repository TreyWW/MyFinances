from __future__ import annotations

from django.urls import path

from . import dashboard

urlpatterns = [
    path(
        "",
        dashboard.dashboard,
        name="dashboard",
    ),
]

app_name = "emails"
