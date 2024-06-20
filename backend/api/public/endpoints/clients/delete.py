from typing import Literal
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.api.public.authentication import BearerAuthentication
from backend.service.clients.delete import delete_client


@api_view(["DELETE"])
@authentication_classes([BearerAuthentication])
@permission_classes([IsAuthenticated])
def client_delete_endpoint(request, client_id):
    response: str | Literal[True] = delete_client(request, client_id)

    if isinstance(response, str):
        return Response({"success": False, "message": response})
    return Response({"success": True, "client_id": client_id})
