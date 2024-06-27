from typing import Literal

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.api.public.decorators import require_scopes
from backend.api.public.serializers.clients import ClientSerializer
from backend.api.public.swagger_ui import TEAM_PARAMETER
from backend.api.public.types import APIRequest
from backend.models import Client
from backend.service.clients.create import create_client


@swagger_auto_schema(
    method="post",
    operation_description="Create a client",
    operation_id="clients_create",
    manual_parameters=[
        TEAM_PARAMETER,
    ],
    query_serializer=ClientSerializer,
    responses={
        201: openapi.Response(
            description="Client created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "client_id": openapi.Schema(type=openapi.TYPE_STRING, description="The ID of the created client"),
                },
            ),
        ),
        403: openapi.Response(
            description="Forbidden",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING, description="You do not have permission to create client under " "this account"
                    ),
                },
            ),
        ),
    },
)
@api_view(["POST"])
@require_scopes(["clients:write"])
def client_create_endpoint(request: APIRequest):

    serializer = ClientSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.team:
        client = serializer.save(organization=request.team)
    else:
        client = serializer.save(user=request.user)

    return Response({"client_id": client.id, "success": True}, status=status.HTTP_201_CREATED)
