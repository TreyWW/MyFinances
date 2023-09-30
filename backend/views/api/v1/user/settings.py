from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from backend.models import *

from django.contrib.auth import get_user_model, logout


@login_required
@require_POST
def toggle_theme(request):
    user_profile = UserSettings.objects.get_or_create(user=request.user).first()

    # Toggle the dark_mode value
    user_profile.dark_mode = not user_profile.dark_mode
    user_profile.save()

    return JsonResponse({"dark_mode": user_profile.dark_mode})
