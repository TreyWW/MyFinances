from django.db.models import QuerySet

from backend.models import UserSettings
from backend.api.public.models import APIAuthToken


def validate_page(page: str | None) -> bool:
    return not page or page in ["profile", "account", "api_keys"]


def get_user_profile(request) -> UserSettings:
    try:
        usersettings = request.user.user_profile
    except UserSettings.DoesNotExist:
        # Create a new UserSettings object
        usersettings = UserSettings.objects.create(user=request.user)
    return usersettings


def get_api_keys(request) -> QuerySet[APIAuthToken]:
    if request.user.logged_in_as_team:
        token = APIAuthToken.objects.filter(team=request.user.logged_in_as_team)
    else:
        token = APIAuthToken.objects.filter(user=request.user)
    return token.filter(active=True).only("created", "name", "last_used", "description", "expires")
