from backend.api.public.models import APIAuthToken
from backend.models import User, Organization, TeamMemberPermission
from backend.service.permissions.scopes import validate_scopes


def edit_member_permissions(receiver: User, team: Organization | None, permissions: list) -> str | None:
    if not validate_receiver(receiver, team):
        return "Invalid key name"

    if not validate_scopes(permissions):
        return "Invalid permissions"

    if not team:
        return "Invalid team, something went wrong"

    user_team_perms: TeamMemberPermission | None = team.permissions.filter(user=receiver).first()

    if not user_team_perms:
        team.permissions.add(TeamMemberPermission.objects.create(user=receiver, team=team, scopes=permissions))
    else:
        user_team_perms.scopes = permissions
        user_team_perms.save()

    return None


def validate_receiver(receiver: User | None, team: Organization | None) -> bool:
    """
    Make sure receiver is in team and not already owner
    """

    if not receiver:
        return False

    if not team:
        return False

    if not team.members.filter(id=receiver.id).first():
        return False

    if not team.leader == receiver:
        return True
    return False
