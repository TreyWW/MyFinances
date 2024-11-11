from functools import wraps

from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework import status

from backend.models import TeamMemberPermission, Organization, Client
from backend.core.api.public.helpers.response import APIResponse

import logging

logger = logging.getLogger(__name__)


def require_scopes(scopes):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            token = request.auth
            if not token:
                logger.info(
                    f"Authentication credentials were not provided in api request |" f" {request.META.get('REMOTE_ADDR', 'Unknown IP')}"
                )
                return APIResponse(False, {"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)

            if request.team_id and not request.team:
                return APIResponse(False, {"detail": "Team not found."}, status=status.HTTP_404_NOT_FOUND)

            if request.team:
                # Check for team permissions based on team_id and scopes
                if not request.team.is_owner(token.user) and not request.team.is_logged_in_as_team(request):
                    team_permissions = TeamMemberPermission.objects.filter(team=request.team, user=token.user).first()
                    if not team_permissions or not all(scope in team_permissions.scopes for scope in scopes):
                        return APIResponse(False, {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

            # Check for global API Key permissions based on token scopes
            if not all(scope in token.scopes for scope in scopes):
                return APIResponse(False, {"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

            token.update_last_used()

            return view_func(request, *args, **kwargs)

        _wrapped_view.required_scopes = scopes
        return _wrapped_view

    return decorator
