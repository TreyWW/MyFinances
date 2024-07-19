from django.urls import include
from django.urls import path
from backend.views.core import settings

urlpatterns = [
    path(
        "",
        settings.teams.teams_dashboard_handler,
        name="dashboard",
    ),
]

app_name = "teams"
