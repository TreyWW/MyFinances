from django.urls import path
from . import kick, switch_team

urlpatterns = [
    path(
        "kick/<int:user_id>",
        kick.kick_user,
        name="kick",
    ),
    path(
        "switch_team/<int:team_id>/",
        switch_team.switch_team,
        name="switch_team",
    )
]

app_name = "teams"
