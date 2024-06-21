from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.db.models import QuerySet
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.api.public.authentication import BearerAuthentication
from backend.api.public.serializers.clients import ClientSerializer
from backend.models import Client
from backend.service.clients.get import fetch_clients


@swagger_auto_schema(
    method="get",
    operation_description="List all clients",
    operation_id="clients_list",
    manual_parameters=[
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
@authentication_classes([BearerAuthentication])
@permission_classes([IsAuthenticated])
def list_clients_endpoint(request):

    # paginator = PageNumberPagination()
    # paginator.page_size = 5

    search_text = request.data.get("search")

    clients: QuerySet[Client] = fetch_clients(request, search_text=search_text)

    # queryset = paginator.paginate_queryset(clients, request)

    serializer = ClientSerializer(clients, many=True)

    return Response({"success": True, "clients": serializer.data})
