from backend.clients.models import DefaultValues, Client
from backend.core.models import Organization, User


def get_user_defaults(client: Client) -> DefaultValues:
    owner: User | Organization = client.owner
    if isinstance(owner, User):
        account_defaults, _ = DefaultValues.objects.get_or_create(user=owner, client=None)
        defaults, created = DefaultValues.objects.get_or_create(user=owner, client=client)
    else:
        account_defaults, _ = DefaultValues.objects.get_or_create(organization=owner, client=None)
        defaults, created = DefaultValues.objects.get_or_create(organization=owner, client=client)

    if created:
        defaults.invoice_date_value = account_defaults.invoice_date_value
        defaults.invoice_date_type = account_defaults.invoice_date_type

        defaults.invoice_due_date_type = account_defaults.invoice_due_date_type
        defaults.invoice_due_date_value = account_defaults.invoice_due_date_value

        defaults.save(update_fields=["invoice_date_value", "invoice_date_type", "invoice_due_date_type", "invoice_due_date_value"])

    return defaults
