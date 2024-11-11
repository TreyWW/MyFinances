from datetime import datetime

from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.core.api.public.decorators import require_scopes
from backend.core.api.public.helpers.deprecate import deprecated
from backend.core.api.public.swagger_ui import TEAM_PARAMETER
from backend.core.api.public.types import APIRequest
from backend.finance.models import Invoice
from backend.core.service.invoices.single.create_pdf import generate_pdf
from backend.core.api.public.helpers.response import APIResponse


@swagger_auto_schema(
    method="get",
    operation_description="Download invoice",
    operation_id="download_invoice",
    manual_parameters=[
        TEAM_PARAMETER,
    ],
    responses={
        200: openapi.Response(
            description="Download invoice by id.",
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
        500: openapi.Response(
            description="Internal error",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Indicates if the operation was successful"),
                    "message": openapi.Schema(type=openapi.TYPE_STRING, description="Internal error occurred while generating PDF"),
                },
            ),
        ),
    },
    deprecated=True,
)
@api_view(["GET"])
@deprecated(datetime(2024, 7, 16), datetime(2024, 7, 16))
@require_scopes(["invoices:read"])
def download(request: APIRequest, id: str) -> HttpResponse | Response:
    try:
        if request.team:
            invoice = Invoice.objects.get(organization=request.team, id=id)
        else:
            invoice = Invoice.objects.get(user=request.user, id=id)
    except Invoice.DoesNotExist:
        return APIResponse(False, {"message": "Invoice not found"}, status=status.HTTP_400_BAD_REQUEST)

    if response := generate_pdf(invoice, "attachment"):
        return response
    return APIResponse(False, {"message": "Error generating PDF"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
