from django.core.exceptions import ValidationError

from backend.core.api.public import APIAuthToken
from backend.models import User, Organization
from backend.core.service.permissions.scopes import validate_scopes


def generate_public_api_key(
    request,
    owner: User | Organization,
    api_key_name: str | None,
    permissions: list,
    *,
    expires=None,
    description=None,
    administrator_toggle: bool = False,
    administrator_type: str | None = None,
) -> tuple[APIAuthToken | None, str]:
    if not validate_name(api_key_name):
        return None, "Invalid key name"

    if not validate_description(description):
        return None, "Invalid description"

    if api_key_exists_under_name(owner, api_key_name):
        return None, "A key with this name already exists in your account"

    if validate_scopes(permissions).failed:  # or not has_permission_to_create(request, owner):
        return None, "Invalid permissions"

    administrator_service_type = None

    if request.user.is_superuser:
        if administrator_toggle:
            if administrator_type not in [option[0] for option in APIAuthToken.AdministratorServiceTypes.choices]:
                return None, "Invalid administration type"
            administrator_service_type = administrator_type

    token = APIAuthToken(
        name=api_key_name,
        description=description,
        expires=expires,
        scopes=permissions,
        administrator_service_type=administrator_service_type,
    )  # type: ignore[arg-type, misc]

    raw_key: str = token.generate_key()

    if isinstance(owner, Organization):
        token.organization = owner
    else:
        token.user = owner

    try:
        token.full_clean()
    except ValidationError as validation_errors:
        field, error_list = next(iter(validation_errors.error_dict.items()))

        field = "Permissions" if field == "scopes" else field.title()

        if isinstance(error_list[0], ValidationError):
            error_message = error_list[0].messages[0]
        else:
            error_message = error_list[0]

        return None, f"{field}: {error_message}"

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


def api_key_exists_under_name(owner: User | Organization, name: str | None) -> bool:
    """
    Check if API key exists under a given name
    """
    return APIAuthToken.filter_by_owner(owner).filter(name=name, active=True).exists()


def has_permission_to_create(request, owner: User | Organization) -> bool:
    if isinstance(owner, User):
        return True

    if owner.permissions.filter(user=request.user).exists() and "api_keys:write" in owner.permissions.get(user=request.user).scopes:
        return True
    return False
