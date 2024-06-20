from backend.models import UserSettings


def validate_page(page: str) -> bool:
    return page in ["profile", "account", "api_keys"]


def get_user_profile(request) -> UserSettings:
    try:
        usersettings = request.user.user_profile
    except UserSettings.DoesNotExist:
        # Create a new UserSettings object
        usersettings = UserSettings.objects.create(user=request.user)
    return usersettings
