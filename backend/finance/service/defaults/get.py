from backend.models import User, Organization
from backend.clients.models import DefaultValues, Client


def get_account_defaults(actor: User | Organization, client: Client | None = None) -> DefaultValues:
    if not client:
        account_defaults = DefaultValues.filter_by_owner(owner=actor).filter(client__isnull=True).first()

        if account_defaults:
            return account_defaults
        return DefaultValues.objects.create(owner=actor, client=None)  # type: ignore[misc]
    return DefaultValues.filter_by_owner(owner=actor).get(client=client)
