from typing import Optional, Tuple
from django.db import transaction
from backend.models import Organization, User


def can_delete_team(team: Organization, user: User) -> Tuple[bool, Optional[str]]:
    """
    Check if a team can be deleted.
    Returns (can_delete: bool, error_message: Optional[str])
    """
    # Check if user is team leader
    if not team.is_owner(user):
        return False, "Only team leaders can delete teams"

    # Check if team has members
    if team.members.count() > 0:
        return False, "All members must be removed before deleting the team"

    return True, None


@transaction.atomic
def delete_team_function(*, team: Organization, user: User) -> Tuple[bool, str]:
    """
    Delete a team if conditions are met.
    Returns (success: bool, message: str)

    This will cascade delete:
    - Team permissions
    - Team invitations
    - Team's invoices and receipts
    - Team's file storage
    - Team's audit logs
    - Team's monthly reports
    - Team's quota usage and overrides
    """
    # Verify deletion is allowed
    can_delete, error = can_delete_team(team, user)
    if not can_delete:
        return False, error
    try:
        team.delete()
        return True
    except Exception as e:
        return False, f"Failed to delete team: {str(e)}"
