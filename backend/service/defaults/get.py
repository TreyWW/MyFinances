from backend.models import DefaultValues, Client
from backend.types.requests import WebRequest


def get_account_defaults(request: WebRequest, client: Client | None = None) -> DefaultValues:
    if not client:
        account_defaults, _ = DefaultValues.objects.get_or_create(user=request.user, client=None)
        return account_defaults
    return DefaultValues.filter_by_owner(owner=request.actor).get(client=client)
