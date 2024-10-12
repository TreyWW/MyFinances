from django.urls import path

from . import kick, switch_team, invites, leave, create, edit_permissions
from .create_user import create_user_endpoint

urlpatterns = [
    path("edit_permissions/", edit_permissions.edit_user_permissions_endpoint, name="edit_permissions"),
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
    path(
        "switch_team/",
        switch_team.switch_team,
        name="switch_team input",
    ),
    path(
        "create_user/",
        create_user_endpoint,
        name="create_user",
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
