from backend.models import User, Team

from backend.api.public.models import APIAuthToken


def get_api_key_by_name(owner: User | Team, key_name: str) -> APIAuthToken | None:
    if isinstance(owner, Team):
        return APIAuthToken.objects.filter(team=owner, name=key_name, active=True).first()
    return APIAuthToken.objects.filter(user=owner, name=key_name, active=True).first()


def get_api_key_by_id(owner: User | Team, key_id: str | int) -> APIAuthToken | None:
    if isinstance(owner, Team):
        return APIAuthToken.objects.filter(team=owner, id=key_id, active=True).first()
    return APIAuthToken.objects.filter(user=owner, id=key_id, active=True).first()
