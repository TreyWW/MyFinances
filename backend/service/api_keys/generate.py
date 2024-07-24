from backend.api.public.models import APIAuthToken
from backend.api.public.permissions import SCOPE_DESCRIPTIONS, SCOPES
from backend.models import User, Organization
from backend.service.permissions.scopes import validate_scopes
from backend.types.htmx import HtmxHttpRequest


def generate_public_api_key(
    request, owner: User | Organization, api_key_name: str | None, permissions: list, *, expires=None, description=None
) -> tuple[APIAuthToken | None, str]:
    if not validate_name(api_key_name):
        return None, "Invalid key name"

    if not validate_description(description):
        return None, "Invalid description"

    if not validate_expiry(expires):
        return None, "Invalid expiry"

    if api_key_exists_under_name(owner, api_key_name):
        return None, "A key with this name already exists in your account"

    if not validate_scopes(permissions) or not has_permission_to_create(request, owner):
        return None, "Invalid permissions"

    token = APIAuthToken(name=api_key_name, description=description, expires=expires, scopes=permissions)  # type: ignore[arg-type, misc]

    raw_key: str = token.generate_key()

    if isinstance(owner, Organization):
        token.organization = owner
    else:
        token.user = owner

    token.save()

    return token, raw_key


def validate_name(name: str | None) -> bool:
    """
    Require name not already exist under account
    """
    if not name:
        return False
    return len(name) <= 64


def validate_description(description: str | None) -> bool:
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


def api_key_exists_under_name(owner: User | Organization, name: str | None) -> bool:
    """
    Check if API key exists under a given name
    """
    return APIAuthToken.filter_by_owner(owner).filter(name=name, active=True).exists()


def has_permission_to_create(request, owner: User | Organization) -> bool:
    if isinstance(owner, User):
        return True

    if "api_keys:write" in owner.permissions.get(user=request.user).scopes:
        return True
    return False
