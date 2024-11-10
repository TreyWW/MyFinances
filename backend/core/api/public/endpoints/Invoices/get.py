from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.core.api.public.decorators import require_scopes
from backend.core.api.public.serializers.invoices import InvoiceSerializer
from backend.core.api.public.swagger_ui import TEAM_PARAMETER
from backend.core.api.public.types import APIRequest
from backend.core.api.public.helpers.response import APIResponse
from backend.finance.models import Invoice


@swagger_auto_schema(
    method="get",
    operation_description="Get invoice",
    operation_id="get_invoice",
    manual_parameters=[
        TEAM_PARAMETER,
    ],
    responses={
        200: openapi.Response(
            description="Get invoice by id.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "invoice": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
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
)
@api_view(["GET"])
@require_scopes(["invoices:read"])
def get_invoices_endpoint(request: APIRequest, id: str) -> Response:
    try:
        if request.team:
            invoices = Invoice.objects.filter(organization=request.team, id=id)
        else:
            invoices = Invoice.objects.filter(user=request.user, id=id)
    except Invoice.DoesNotExist:
        return APIResponse(False, {"message": "Invoice not found"}, status=status.HTTP_400_BAD_REQUEST)

    serializer = InvoiceSerializer(invoices, many=True)

    return APIResponse(True, {"invoice": serializer.data}, status=status.HTTP_200_OK)
