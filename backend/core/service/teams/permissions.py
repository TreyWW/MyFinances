from backend.models import User, Organization, TeamMemberPermission
from backend.core.service.permissions.scopes import validate_scopes
from backend.core.utils.dataclasses import BaseServiceResponse


class EditMemberPermissionsServiceResponse(BaseServiceResponse[None]):
    response: None = None


def edit_member_permissions(receiver: User, team: Organization | None, permissions: list) -> EditMemberPermissionsServiceResponse:
    if not validate_receiver(receiver, team):
        return EditMemberPermissionsServiceResponse(error_message="Invalid key name")

    if (scopes_response := validate_scopes(permissions)).failed:
        return EditMemberPermissionsServiceResponse(error_message=scopes_response.error)

    if not team:
        return EditMemberPermissionsServiceResponse(error_message="Invalid team, something went wrong")

    user_team_perms: TeamMemberPermission | None = team.permissions.filter(user=receiver).first()

    if not user_team_perms:
        team.permissions.add(TeamMemberPermission.objects.create(user=receiver, team=team, scopes=permissions))
    else:
        user_team_perms.scopes = permissions
        user_team_perms.save()

    return EditMemberPermissionsServiceResponse(True)


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
