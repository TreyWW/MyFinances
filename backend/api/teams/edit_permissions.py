from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import web_require_scopes
from backend.models import User
from backend.service.api_keys.delete import delete_api_key
from backend.service.api_keys.generate import generate_public_api_key

from backend.service.api_keys.get import get_api_key_by_id
from backend.service.permissions.scopes import get_permissions_from_request
from backend.api.public.models import APIAuthToken
from backend.service.teams.permissions import edit_member_permissions
from backend.types.requests import WebRequest


@require_http_methods(["POST"])
@web_require_scopes("team_permissions:write")
def edit_user_permissions_endpoint(request: WebRequest) -> HttpResponse:
    permissions: list = get_permissions_from_request(request)
    user_id = request.POST.get("user_id")

    receiver: User | None = User.objects.filter(id=user_id).first()

    if receiver:
        error = edit_member_permissions(receiver, request.user.logged_in_as_team, permissions)
    else:
        error = "Something went wrong"

    if error:
        messages.error(request, error)
    else:
        messages.success(request, "User permissions saved successfully")
    return render(request, "base/toast.html")
