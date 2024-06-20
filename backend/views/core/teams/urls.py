from django.urls import include
from django.urls import path
from backend.views.core import settings

urlpatterns = [
    path(
        "",
        settings.teams.teams_dashboard,
        name="dashboard",
    ),
    path(
        "permissions/",
        settings.teams.manage_permissions_dashboard,
        name="permissions",
    ),
]

app_name = "teams"
