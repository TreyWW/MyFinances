from functools import wraps

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from backend.models import TeamMemberPermission, Team, Client


def require_scopes(scopes):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = request.auth
            if not token:
                return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

            team_id = request.query_params.get("team_id")
            if team_id:
                team = Team.objects.filter(id=team_id).first()
                if not team:
                    return Response({"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)
                # Check for team permissions based on team_id and scopes

                if not team.is_owner(token.user):
                    team_permissions = TeamMemberPermission.objects.filter(team_id=team_id, user=token.user).first()
                    if not team_permissions or not all(scope in team_permissions.scopes for scope in scopes):
                        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

            # Check for global API Key permissions based on token scopes
            if not all(scope in token.scopes for scope in scopes):
                return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

            return view_func(request, *args, **kwargs)

        _wrapped_view.required_scopes = scopes
        return _wrapped_view

    return decorator


def handle_team_context(view_func):
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        team_id = request.query_params.get("team_id")

        if not team_id:
            # No team_id provided, proceed with user context
            return view_func(request, *args, **kwargs)

        team = Team.objects.filter(id=team_id).first()

        if not team:
            return Response({"success": False, "error": "Team not found"}, status=404)

        # Check if the user is a member of the team
        if request.user.is_authenticated and (
            request.user.teams_joined.filter(id=team_id).exists() or request.user.teams_leader_of.filter(id=team_id).exists()
        ):
            return view_func(request, team=team, *args, **kwargs)
        else:
            raise PermissionDenied("You are not a member of this team")

    return wrapped_view
