from django.contrib import messages
from django.shortcuts import get_object_or_404

from backend.decorators import web_require_scopes
from django.views.decorators.http import require_POST

from backend.models import Organization
from backend.core.service.teams.delete_team import delete_team_function
from django.shortcuts import render


@require_POST
@web_require_scopes("team:delete", True, True)
def delete_team(request, team_id):
    """
    API endpoint for deleting a team.

    This follows the same pattern as the kick_user API endpoint.
    """
    team = get_object_or_404(Organization, id=team_id)

    # Check if user is logged into this team
    if not request.user.logged_in_as_team or request.user.logged_in_as_team.id != team.id:
        messages.error(request, "User is not logged in as a team")
        return render(request, "partials/messages_list.html")

    # Check if user is team leader
    if team.leader != request.user:
        messages.error(request, "User is not a team leader")
        return render(request, "partials/messages_list.html")

    # Check if team has no members
    if team.members.count() > 0:
        messages.error(request, "Team has members. Remove all members before deleting")
        return render(request, "partials/messages_list.html")

    # Delete the team using the service layer
    success = delete_team_function(team=team, user=request.user)

    if success:
        response = render(request, "partials/messages_list.html")
        response["HX-Refresh"] = "true"
        return response
    else:
        messages.error(request, "Error deleting this team")
        return render(request, "partials/messages_list.html")
