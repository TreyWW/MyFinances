from django.urls import path, include

urlpatterns = [
    path("base/", include("backend.api.base.urls")),
    path("teams/", include("backend.api.teams.urls")),
    path("receipts/", include("backend.api.receipts.urls")),
    path("invoices/", include("backend.api.invoices.urls")),
    path("clients/", include("backend.api.clients.urls")),
    path("settings/", include("backend.api.settings.urls")),
]

app_name = "api"
