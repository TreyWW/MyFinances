from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.clients.models import Client
from backend.core.api.public.decorators import require_scopes
from backend.core.api.public.helpers.response import APIResponse
from backend.core.api.public.serializers.invoices import InvoiceSerializer
from backend.core.api.public.swagger_ui import TEAM_PARAMETER
from backend.core.api.public.types import APIRequest
from backend.finance.models import InvoiceProduct


def get_client(request: APIRequest) -> Client | None:
    if request.team:
        client = Client.objects.get(organization=request.team, id=request.data.get("client_id"))  # type: ignore[misc]
        return client
    elif request.user:
        client = Client.objects.get(user=request.user, id=request.data.get("client_id"))  # type: ignore[misc]
        return client
    return None


def get_products(request: APIRequest) -> list[dict] | None:
    product_id_list = request.query_params.get("product_id", "").split(",")
    product_ids = [int(id.strip()) for id in product_id_list if id.strip().isdigit()]

    items_data = []
    for product_id in product_ids:
        if request.team:
            product = InvoiceProduct.objects.get(organization=request.team, id=product_id)
        else:
            product = InvoiceProduct.objects.get(user=request.user, id=product_id)

        product_data = {
            "name": product.name,
            "description": product.description,
            "hours": product.quantity,
            "price_per_hour": product.rate,
            "price": (product.rate * product.quantity) if product.rate else product.quantity,
        }
        items_data.append(product_data)

    return items_data


@swagger_auto_schema(
    method="post",
    operation_description="Create invoice",
    operation_id="create_invoice",
    manual_parameters=[
        TEAM_PARAMETER,
        openapi.Parameter(
            "product_id",
            openapi.IN_QUERY,
            description="Id of a product",
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_INTEGER),
        ),
        openapi.Parameter(
            "client_id",
            openapi.IN_QUERY,
            description="Id of a client",
            type=openapi.TYPE_INTEGER,
        ),
    ],
    request_body=InvoiceSerializer,
    responses={
        201: openapi.Response(
            description="Invoice created successfully",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "invoice_id": openapi.Schema(type=openapi.TYPE_STRING, description="The ID of the created invoice"),
                },
            ),
        ),
        400: openapi.Response(
            description="Bad request",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "message": openapi.Schema(
                        type=openapi.TYPE_STRING, description="Your request is missing fields or fields are incorrect"
                    ),
                },
            ),
        ),
    },
    partial=True,
)
@api_view(["POST"])
@require_scopes(["invoices:write"])
def create_invoice_endpoint(request: APIRequest) -> Response:
    for key, value in request.query_params.items():
        request.data[key] = value

    serializer = InvoiceSerializer(data=request.data)

    if not serializer.is_valid():
        return APIResponse(False, serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if "client_id" in request.data and request.data["client_id"]:
        try:
            client = get_client(request)
            serializer.validated_data["client_to"] = client
        except Client.DoesNotExist:
            return APIResponse(False, "Client not found", status=status.HTTP_400_BAD_REQUEST)

    if "product_id" in request.data and request.data["product_id"]:
        try:
            items_data = get_products(request)
            serializer.validated_data["items"] = items_data
        except InvoiceProduct.DoesNotExist:
            return APIResponse(False, "InvoiceProduct not found", status=status.HTTP_400_BAD_REQUEST)

    if request.team:
        invoice = serializer.save(organization=request.team)
    else:
        invoice = serializer.save(user=request.user)

    return APIResponse(True, {"invoice_id": invoice.id}, status=status.HTTP_201_CREATED)
