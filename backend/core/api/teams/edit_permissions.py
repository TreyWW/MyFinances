from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import User
from backend.core.service.permissions.scopes import get_permissions_from_request
from backend.core.service.teams.permissions import edit_member_permissions
from backend.core.types.requests import WebRequest


@require_http_methods(["POST"])
@web_require_scopes("team_permissions:write")
def edit_user_permissions_endpoint(request: WebRequest) -> HttpResponse:
    permissions: list = get_permissions_from_request(request)
    user_id = request.POST.get("user_id")

    receiver: User | None = User.objects.filter(id=user_id).first()

    if not receiver:
        messages.error(request, "Invalid user")
        return render(request, "base/toast.html")

    edit_response = edit_member_permissions(receiver, request.user.logged_in_as_team, permissions)

    if edit_response.success:
        messages.success(request, "User permissions saved successfully")
    else:
        messages.error(request, edit_response.error)
    return render(request, "base/toast.html")
