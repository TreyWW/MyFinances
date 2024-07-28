from backend.models import DefaultValues, Client, User, Organization
from backend.types.requests import WebRequest


def get_account_defaults(actor: User | Organization, client: Client | None = None) -> DefaultValues:
    if not client:
        account_defaults: DefaultValues | None
        if not (account_defaults := DefaultValues.filter_by_owner(owner=actor).filter(client__isnull=True).first()):
            account_defaults = DefaultValues.objects.create(owner=request.actor, client=None)  # type: ignore[misc]
        return account_defaults
    return DefaultValues.filter_by_owner(owner=actor).get(client=client)
