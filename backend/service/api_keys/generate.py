from backend.api.public.models import APIAuthToken
from backend.api.public.permissions import SCOPE_DESCRIPTIONS, SCOPES
from backend.models import User, Team
from backend.types.htmx import HtmxHttpRequest


def generate_public_api_key(
    owner: User | Team, api_key_name: str, permissions: list, *, expires=None, description=None
) -> APIAuthToken | str:
    if not validate_name(api_key_name):
        return "Invalid key name"

    if not validate_description(description):
        return "Invalid description"

    if not validate_expiry(expires):
        return "Invalid expiry"

    if api_key_exists_under_name(owner, api_key_name):
        return "A key with this name already exists in your account"

    if not validate_scopes(permissions):
        return "Invalid permissions"

    token = APIAuthToken(name=api_key_name, description=description, expires=expires, scopes=permissions)

    if isinstance(owner, Team):
        token.team = owner
    else:
        token.user = owner

    token.save()

    return token


def get_permissions_from_request(request: HtmxHttpRequest) -> list:
    scopes = [
        f"{group}:{perm}"
        for group, items in SCOPE_DESCRIPTIONS.items()
        if (perm := request.POST.get(f"permission_{group}")) in items["options"]
    ]

    scopes.extend(f"{group}:read" for group, items in SCOPE_DESCRIPTIONS.items() if request.POST.get(f"permission_{group}") == "write")

    return scopes


def validate_scopes(permissions: list[str]) -> bool:
    """
    Validate permissions are valid
    """
    if not permissions:
        return False

    for permission in permissions:
        if permission not in SCOPES:
            return False
    return True


def validate_name(name: str) -> bool:
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


def api_key_exists_under_name(owner: User | Team, name: str) -> bool:
    """
    Check if API key exists under a given name
    """
    if isinstance(owner, Team):
        return APIAuthToken.objects.filter(team=owner, name=name, active=True).exists()
    return APIAuthToken.objects.filter(user=owner, name=name, active=True).exists()