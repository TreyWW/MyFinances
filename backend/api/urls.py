from __future__ import annotations

from django.urls import include
from django.urls import path

from backend.api.settings.defaults import handle_client_defaults_endpoints, remove_client_default_logo_endpoint

urlpatterns = [
    path("clients/", include("backend.clients.api.urls", namespace="clients")),
    path("finance/", include("backend.finance.api.urls", namespace="finance")),
    path(
        "settings/",
        include(
            (
                [
                    path("client_defaults/<int:client_id>/", handle_client_defaults_endpoints, name="client_defaults"),
                    path("client_defaults/", handle_client_defaults_endpoints, name="client_defaults without client"),
                    path(
                        "client_defaults/remove_default_logo/",
                        remove_client_default_logo_endpoint,
                        name="client_defaults remove logo without client",
                    ),
                    path(
                        "client_defaults/remove_default_logo/<int:client_id>",
                        remove_client_default_logo_endpoint,
                        name="client_defaults remove logo",
                    ),
                ],
                "settings",
            ),
            namespace="settings",
        ),
    ),
]

app_name = "api"
