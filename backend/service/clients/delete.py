from typing import Literal

from backend.service.clients.validate import validate_client
from django.core.exceptions import ValidationError, PermissionDenied

from backend.models import Client, AuditLog


def delete_client(request, client_id) -> str | Literal[True]:
    """

    :param request:
    :param client_id:
    :returns: True if success else str if error
    """
    try:
        client: Client = validate_client(request, client_id)
    except Client.DoesNotExist:
        return "This client does not exist"
    except ValidationError:
        return "Invalid client id"
    except PermissionDenied:
        return "You do not have permission to delete this client"

    AuditLog.objects.create(user=request.user, action=f'Deleted the client "{client.name}" (#{client.id})')

    client.delete()
    return True
