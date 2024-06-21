from django.utils import timezone
from backend.api.public.models import APIAuthToken
from backend.models import User


def generate_public_api_key(user: User, api_key_name, *, expires=None, description=None) -> APIAuthToken | str:
    if not validate_name(user, api_key_name):
        return "Invalid key name"

    if not validate_description(description):
        return "Invalid description"

    if not validate_expiry(expires):
        return "Invalid expiry"

    if api_key_exists_under_name(user, api_key_name):
        return "A key with this name already exists in your account"

    return APIAuthToken.objects.create(user=user, name=api_key_name, description=description, expires=expires)


def validate_name(user: User, name: str) -> bool:
    """
    Require name not already exist under account
    """
    if not name:
        return False
    return len(name) <= 64


def validate_description(description: str) -> bool:
    """
    Accept any description
    Reject description longer than 255 characters
    """
    return not description or len(description) <= 255


def validate_expiry(expires: str | int) -> bool:
    """
    Accept no expiry
    Accept expiry < 256
    """

    if not expires:
        return True

    try:
        expires = int(expires)
    except ValueError:
        return False

    if expires < 0 or expires > 255:
        return False

    return True


def api_key_exists_under_name(user: User, name: str) -> bool:
    """
    Check if API key exists under a given name
    """
    return APIAuthToken.objects.filter(user=user, name=name, active=True).exists()
