from backend.models import User, Organization

from backend.api.public.models import APIAuthToken


def get_api_key_by_name(owner: User | Organization, key_name: str) -> APIAuthToken | None:
    return APIAuthToken.filter_by_owner(owner).filter(name=key_name, active=True).first()


def get_api_key_by_id(owner: User | Organization, key_id: str | int) -> APIAuthToken | None:
    return APIAuthToken.filter_by_owner(owner).filter(id=key_id, active=True).first()
