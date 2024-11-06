from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import QuerySet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.core.api.public.decorators import require_scopes
from backend.core.api.public.helpers.response import APIResponse
from backend.core.api.public.serializers.clients import ClientSerializer
from backend.core.api.public.swagger_ui import TEAM_PARAMETER
from backend.core.api.public.types import APIRequest
from backend.core.service.clients.get import fetch_clients, FetchClientServiceResponse

from backend.models import Organization


@swagger_auto_schema(
    method="get",
    operation_description="List all clients",
    operation_id="clients_list",
    manual_parameters=[
        TEAM_PARAMETER,
        openapi.Parameter("order_by", openapi.IN_QUERY, description="field you want to order by to", type=openapi.TYPE_STRING),
        openapi.Parameter("search", openapi.IN_QUERY, description="field you want to search by", type=openapi.TYPE_STRING),
    ],
    responses={
        200: openapi.Response(
            description="List of clients",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "clients": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Items(type=openapi.TYPE_OBJECT)),
                },
            ),
        )
    },
)
@api_view(["GET"])
@require_scopes(["clients:read"])
def list_clients_endpoint(request: APIRequest):
    # paginator = PageNumberPagination()
    # paginator.page_size = 5

    search_text = request.data.get("search")

    clients: FetchClientServiceResponse = fetch_clients(request, search_text=search_text, team=request.team)

    # queryset = paginator.paginate_queryset(clients, request)

    serializer = ClientSerializer(clients.response, many=True)
    return APIResponse(True, {"clients": serializer.data})
