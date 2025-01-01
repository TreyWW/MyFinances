from backend.models import User, Organization
from backend.models import FinanceDefaultValues, Client


def get_account_defaults(actor: User | Organization, client: Client | None = None) -> FinanceDefaultValues:
    if not client:
        account_defaults = FinanceDefaultValues.filter_by_owner(owner=actor).filter(client__isnull=True).first()

        if account_defaults:
            return account_defaults
        return FinanceDefaultValues.objects.create(owner=actor, client=None)  # type: ignore[misc]
    return FinanceDefaultValues.filter_by_owner(owner=actor).get(client=client)
