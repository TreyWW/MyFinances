from django.db.models import QuerySet

from backend.models import UserSettings
from backend.api.public.models import APIAuthToken


def validate_page(page: str) -> bool:
    return not page or page in ["profile", "account", "api_keys"]


def get_user_profile(request) -> UserSettings:
    try:
        usersettings = request.user.user_profile
    except UserSettings.DoesNotExist:
        # Create a new UserSettings object
        usersettings = UserSettings.objects.create(user=request.user)
    return usersettings


def get_api_keys(request) -> QuerySet[APIAuthToken]:
    return APIAuthToken.objects.filter(user=request.user, active=True).only("created", "name", "last_used", "description", "expires")
