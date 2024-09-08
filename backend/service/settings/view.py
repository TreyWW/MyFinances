from django.db.models import QuerySet

from backend.models import UserSettings
from backend.models import DefaultValues
from backend.api.public.models import APIAuthToken
from backend.types.requests import WebRequest


def validate_page(page: str | None) -> bool:
    return not page or page in ["profile", "account", "api_keys", "account_defaults"]


def get_user_profile(request: WebRequest) -> UserSettings:
    try:
        usersettings = request.user.user_profile
    except UserSettings.DoesNotExist:
        # Create a new UserSettings object
        usersettings = UserSettings.objects.create(user=request.user)
    return usersettings


def get_api_keys(request: WebRequest) -> QuerySet[APIAuthToken]:
    return APIAuthToken.filter_by_owner(request.actor).filter(active=True).only("created", "name", "last_used", "description", "expires")
