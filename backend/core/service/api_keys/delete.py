from backend.models import User, Organization
from backend.core.service.api_keys.get import get_api_key_by_name
from backend.core.api.public import APIAuthToken


def delete_api_key(request, owner: User | Organization, key: str | None | APIAuthToken) -> bool | str:
    if isinstance(owner, Organization) and "api_keys:write" not in owner.permissions.get(user=request.user).scopes:
        return "No permission to delete key"

    if not isinstance(key, APIAuthToken):
        key: APIAuthToken | None = get_api_key_by_name(owner, key)  # type: ignore[no-redef, arg-type]

    if not key:
        return "Key not found"

    key.deactivate()  # type: ignore[union-attr]

    return True
