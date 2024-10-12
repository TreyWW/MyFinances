from backend.core.api.public.permissions import SCOPE_DESCRIPTIONS, SCOPES
from backend.core.types.requests import WebRequest
from backend.core.utils.dataclasses import BaseServiceResponse


class PermissionScopesServiceResponse(BaseServiceResponse[None]):
    response: None = None


def get_permissions_from_request(request: WebRequest) -> list:
    scopes = [
        f"{group}:{perm}"
        for group, items in SCOPE_DESCRIPTIONS.items()
        if (perm := request.POST.get(f"permission_{group}")) in items["options"]
    ]

    scopes.extend(f"{group}:read" for group, items in SCOPE_DESCRIPTIONS.items() if request.POST.get(f"permission_{group}") == "write")

    return scopes


def validate_scopes(permissions: list[str]) -> PermissionScopesServiceResponse:
    """
    Validate permissions are valid
    """
    if not permissions:
        return PermissionScopesServiceResponse(True)

    invalid_permissions: list[str] = [permission for permission in permissions if permission not in SCOPES]

    if invalid_permissions:
        return PermissionScopesServiceResponse(False, error_message=f"Invalid permissions: {', '.join(invalid_permissions)}")

    return PermissionScopesServiceResponse(True)
