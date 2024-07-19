from backend.models import DefaultValues, Client
from backend.types.requests import WebRequest


def get_account_defaults(request: WebRequest, client: Client | None = None) -> DefaultValues:
    if not client:
        account_defaults: DefaultValues
        if not (account_defaults := DefaultValues.filter_by_owner(owner=request.actor).filter(client__isnull=True).first()):
            account_defaults = DefaultValues.objects.create(owner=request.actor, client=None)
        return account_defaults
    return DefaultValues.filter_by_owner(owner=request.actor).get(client=client)
