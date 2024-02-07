from django.urls import path

from . import kick, switch_team, invites, leave, create

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
    ),
    # INVITES #
    path(
        "invite/",
        invites.send_user_team_invite,
        name="invite",
    ),
    path(
        "join/<str:code>/accept/",
        invites.accept_team_invite,
        name="join accept",
    ),
    path(
        "join/<str:code>/decline/",
        invites.decline_team_invite,
        name="join decline",
    ),
    # LEAVE TEAM #
    path(
        "leave/<int:team_id>/confirm/",
        leave.leave_team_confirmed,
        name="leave confirm",
    ),
    path(
        "create/",
        create.create_team,
        name="create",
    ),
    path("get_dropdown/", switch_team.get_dropdown, name="get_dropdown"),
]

app_name = "teams"
