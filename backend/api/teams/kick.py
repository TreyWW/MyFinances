from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect

from backend.models import User, Team


def kick_user(request: HttpRequest, user_id):
    user: User | None = User.objects.filter(id=user_id).first()
    confirmation_text = request.POST.get("confirmation_text")
    if not user:
        messages.error(request, "User not found")
        return redirect("user settings teams")

    if confirmation_text != f"i confirm i want to kick {user.username}":
        messages.error(request, "Invalid confirmation")
        return redirect("user settings teams")

    team: Team | None = user.teams_joined.first()
    if not team:
        messages.error(request, "User is not apart of your team")
        return redirect("user settings teams")

    if team.leader != request.user:
        messages.error(request, "You don't have the required permissions to kick this user")
        return redirect("user settings teams")

    team.members.remove(user)
    messages.success(request, f"Successfully kicked {user.username}")

    return redirect("user settings teams")
