from backend.models import User
from backend.service.api_keys.get import get_api_key_by_name
from backend.api.public.models import APIAuthToken


def delete_api_key(user: User, key: str | APIAuthToken) -> bool | str:
    if not isinstance(key, APIAuthToken):
        key: APIAuthToken | None = get_api_key_by_name(user, key)  # type: ignore[no-redef]

    if not key:
        return "Key not found"

    key: APIAuthToken

    key.deactivate()

    return True
