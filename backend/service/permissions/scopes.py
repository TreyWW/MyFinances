from backend.api.public.permissions import SCOPE_DESCRIPTIONS, SCOPES
from backend.types.requests import WebRequest


def get_permissions_from_request(request: WebRequest) -> list:
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
