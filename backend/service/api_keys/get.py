from backend.models import User

from backend.api.public.models import APIAuthToken


def get_api_key_by_name(user: User, key_name: str) -> APIAuthToken | None:
    return APIAuthToken.objects.filter(user=user, name=key_name, active=True).first()


def get_api_key_by_id(user: User, key_id: str | int) -> APIAuthToken | None:
    return APIAuthToken.objects.filter(user=user, id=key_id, active=True).first()
