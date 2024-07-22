from django.core.exceptions import ValidationError, PermissionDenied
from django.db.models import QuerySet, Manager
from django.shortcuts import get_object_or_404

from backend.models import Client


def validate_client(request, client_id: str | int, *, get_defaults: bool = False) -> Client:
    """
    Validates the client based on the client_id and user access.

    :param request: HttpRequest object
    :param client_id: str or int - ID of the client to validate
    :param get_defaults: bool - whether to fetch related client_defaults
    :raises ValidationError: if client_id is not a valid integer
    :raises PermissionDenied: if the user does not have access to the client
    :return: Client instance
    """
    try:
        client_id = int(client_id)
    except (ValueError, TypeError):
        raise ValidationError("Invalid client ID")

    client_query = Client.objects.all()

    if get_defaults:
        client_query = client_query.select_related("default_values")

    client = client_query.get(id=client_id)

    if not client.has_access(request.user):
        raise PermissionDenied

    return client


def validate_client_create(client_details) -> str | None:
    if not client_details.get("name"):
        return "Please provide at least a client name"

    if len(client_details.get("name")) < 3:
        return "Client name must be at least 3 characters"

    if client_details.get("is_representative") and not client_details.get("company"):
        return "Please provide a company name if you are creating a representative"

    if client_details.get("address") and not 3 < len(client_details.get("address")) < 84:
        return "Please provide a valid address between 3 and 84 characters"

    return None
