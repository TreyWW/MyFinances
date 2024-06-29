from backend.models import User, Team
from backend.service.api_keys.get import get_api_key_by_name
from backend.api.public.models import APIAuthToken


def delete_api_key(owner: User | Team, key: str | None | APIAuthToken) -> bool | str:
    if not isinstance(key, APIAuthToken):
        key: APIAuthToken | None = get_api_key_by_name(owner, key)  # type: ignore[no-redef, arg-type]

    if not key:
        return "Key not found"

    key.deactivate()  # type: ignore[union-attr]

    return True
