from django.urls import path

from backend.core.views.settings.teams import teams_dashboard_handler

urlpatterns = [
    path(
        "",
        teams_dashboard_handler,
        name="dashboard",
    ),
]

app_name = "teams"
