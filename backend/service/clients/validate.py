from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import QuerySet, Manager

from backend.models import Client


def validate_client(request, client_id: str | int, *, get_defaults: bool = False) -> Client:
    """
    :raises ValidationError:
    :raises PermissionDenied:
    :raises Client.DoesNotExist:
    :return: Client
    """
    try:
        int(client_id)
    except ValueError:
        raise ValidationError("Invalid client ID")

    client_query = Client.objects

    if get_defaults:
        client_query = client_query.select_related("client_defaults")

    client = client_query.get(id=client_id)  # may raise Client.DoesNotExist

    if not client.has_access(request.user):
        raise PermissionDenied

    return client
