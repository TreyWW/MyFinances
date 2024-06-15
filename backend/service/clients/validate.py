from django.core.exceptions import ValidationError, PermissionDenied

from backend.models import Client


def validate_client(request, client_id: str | int) -> Client:
    """
    :raises ValidationError:
    :raises PermissionDenied:
    :raises Client.DoesNotExist:
    :return: Client
    """
    try:
        int(client_id)
    except ValueError:
        raise ValidationError

    client = Client.objects.get(id=client_id)  # may raise DoesNotExist

    if not client.has_access(request.user):
        raise PermissionDenied

    return client
