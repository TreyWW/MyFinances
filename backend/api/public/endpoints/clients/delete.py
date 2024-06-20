from typing import Literal

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.api.public.authentication import BearerAuthentication
from backend.service.clients.delete import delete_client


@swagger_auto_schema(
    method="delete",
    operation_description="Delete a client",
    operation_id="clients_delete",
    responses={
        200: openapi.Response(
            description="Client deleted successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "client_id": openapi.Schema(type=openapi.TYPE_STRING, description="The ID of the deleted client"),
                },
            ),
        ),
        403: openapi.Response(
            description="Forbidden",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="You do not have permission to delete this client"),
                },
            ),
        ),
        404: openapi.Response(
            description="Not Found",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="This client does not exist"),
                },
            ),
            examples={
                "application/json": {
                    "success": False,
                    "message": "This client does not exist",
                }
            },
        ),
    },
)
@api_view(["DELETE"])
@authentication_classes([BearerAuthentication])
@permission_classes([IsAuthenticated])
def client_delete_endpoint(request, client_id: int):
    response: str | Literal[True] = delete_client(request, client_id)

    if isinstance(response, str):
        return Response({"success": False, "message": response}, status=403 if "do not have permission" in response else 404)
    return Response({"success": True, "client_id": client_id}, status=200)
