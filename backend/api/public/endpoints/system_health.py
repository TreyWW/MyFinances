from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db import connection, OperationalError
from django.core.cache import cache

from rest_framework.decorators import api_view, permission_classes

from core.api.public.permissions import IsSuperuser
from core.api.public.helpers.response import APIResponse


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
        return APIResponse(False, "User is not permitted to view internal information", status=403)

    problems = []

    try:
        connection.ensure_connection()
    except OperationalError:
        problems.append({"id": "database", "message": "database failed to connect"})

    try:
        cache._cache.get_client().ping()
    except ConnectionError:
        problems.append({"id": "redis", "message": "redis failed to connect"})

    return APIResponse({"problems": problems, "healthy": not bool(problems)})
