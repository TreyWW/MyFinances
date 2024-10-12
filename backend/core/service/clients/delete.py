from backend.core.service.clients.validate import validate_client
from django.core.exceptions import ValidationError, PermissionDenied

from backend.models import Client, AuditLog
from backend.core.utils.dataclasses import BaseServiceResponse


class DeleteClientServiceResponse(BaseServiceResponse[None]):
    response: None = None


def delete_client(request, client_id) -> DeleteClientServiceResponse:
    """

    :param request:
    :param client_id:
    :returns: True if success else str if error
    """
    try:
        client: Client = validate_client(request, client_id)
    except Client.DoesNotExist:
        return DeleteClientServiceResponse(False, error_message="This client does not exist")
    except ValidationError:
        return DeleteClientServiceResponse(False, error_message="Invalid client id")
    except PermissionDenied:
        return DeleteClientServiceResponse(False, error_message="You do not have permission to delete this client")

    AuditLog.objects.create(user=request.user, action=f'Deleted the client "{client.name}" (#{client.id})')

    client.delete()
    return DeleteClientServiceResponse(True)
