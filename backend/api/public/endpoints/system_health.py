from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import requests
from django.db import connection, OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from backend.api.public.permissions import IsSuperuser


@swagger_auto_schema(
    method="get",
    operation_description="Check the system's health by verifying database and external API connections.",
    responses={
        200: openapi.Response(
            description="System health check result",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "problems": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_STRING, description="Problem ID"),
                                "message": openapi.Schema(type=openapi.TYPE_STRING, description="Problem message"),
                            },
                        ),
                    ),
                    "healthy": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates overall system health"),
                },
            ),
            examples={
                "application/json": {
                    "problems": [
                        {"id": "database", "message": "database failed to connect"},
                        {"id": "forex_api", "message": "forex api failed to connect"},
                    ],
                    "healthy": False,
                }
            },
        )
    },
)
@api_view(["GET"])
@permission_classes([IsSuperuser])
def system_health_endpoint(request):
    if not request.user or not request.user.is_superuser:
        return Response({"success": False, "message": "User is not permitted to view internal information"}, status=403)

    problems = []

    try:
        connection.ensure_connection()
    except OperationalError:
        problems.append({"id": "database", "message": "database failed to connect"})

    try:
        forex_api_response = requests.get("https://theforexapi.com/", timeout=2)
        if forex_api_response.status_code != 200:
            raise OperationalError
    except (requests.ReadTimeout, OperationalError):
        problems.append({"id": "forex_api", "message": "forex api failed to connect"})

    return Response({"problems": problems, "healthy": not bool(problems)})
