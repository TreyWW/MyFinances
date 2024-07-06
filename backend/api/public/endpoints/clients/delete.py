from typing import Literal

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.api.public.decorators import require_scopes
from backend.api.public.swagger_ui import TEAM_PARAMETER
from backend.api.public.types import APIRequest
from backend.service.clients.delete import delete_client


@swagger_auto_schema(
    method="delete",
    operation_description="Delete a client",
    operation_id="clients_delete",
    manual_parameters=[
        TEAM_PARAMETER,
    ],
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
@require_scopes(["clients:write"])
def client_delete_endpoint(request: APIRequest, id: str):
    response: str | Literal[True] = delete_client(request, id)

    if isinstance(response, str):
        return Response({"success": False, "message": response}, status=403 if "do not have permission" in response else 404)
    return Response({"success": True, "client_id": id}, status=200)
