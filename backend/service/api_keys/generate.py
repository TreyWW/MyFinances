from django.utils import timezone
from backend.api.public.models import APIAuthToken
from backend.api.public.permissions import SCOPE_DESCRIPTIONS
from backend.models import User
from backend.types.htmx import HtmxHttpRequest


def generate_public_api_key(user: User, api_key_name: str, permissions: list, *, expires=None, description=None) -> APIAuthToken | str:
    if not validate_name(user, api_key_name):
        return "Invalid key name"

    if not validate_description(description):
        return "Invalid description"

    if not validate_expiry(expires):
        return "Invalid expiry"

    if api_key_exists_under_name(user, api_key_name):
        return "A key with this name already exists in your account"

    if not validate_scopes(permissions):
        return "Invalid permissions"

    return APIAuthToken.objects.create(user=user, name=api_key_name, description=description, expires=expires, scopes=permissions)


def get_permissions_from_request(request: HtmxHttpRequest) -> list:
    scopes: list = []

    for group, items in SCOPE_DESCRIPTIONS.items():
        group_perm = request.POST.get(f"permission_{group}")
        options: list[str] = items.get("options", {}.keys())

        if group_perm not in options:
            continue

        if group_perm == "write":
            scopes.append(f"{group}:read")
        scopes.append(f"{group}:{group_perm}")

    return scopes


def validate_scopes(permissions: list[str]) -> bool:
    """
    Validate permissions are valid
    """
    if not permissions:
        return False

    for permission in permissions:
        perm_split = permission.split(":")

        if not len(perm_split) == 2:
            return False

        group = perm_split[0]
        option = perm_split[1]

        scope_group = SCOPE_DESCRIPTIONS.get(group)

        if not scope_group:
            return False

        scope_group_options = scope_group.get("options")

        if not option in scope_group_options.keys():
            return False
    return True


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
