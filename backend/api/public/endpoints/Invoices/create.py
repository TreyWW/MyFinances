from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from backend.api.public.decorators import require_scopes, handle_team_context
from backend.api.public.swagger_ui import TEAM_PARAMETER
from backend.service.invoices.create.create import invoice_save


@swagger_auto_schema(
    method="post",
    operation_description="Create invoice",
    operation_id="create_invoice",
    manual_parameters=[
        openapi.Parameter(
            "client_name",
            openapi.IN_QUERY,
            description="Name of the client",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "client_company",
            openapi.IN_QUERY,
            description="Company of the client",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "client_address",
            openapi.IN_QUERY,
            description="Address of the client",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "client_city",
            openapi.IN_QUERY,
            description="City of the client",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "client_county",
            openapi.IN_QUERY,
            description="County of the client",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "client_country",
            openapi.IN_QUERY,
            description="Country of the client",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "client_is_representative",
            openapi.IN_QUERY,
            description="Is the client a representative",
            type=openapi.TYPE_BOOLEAN,
        ),
        openapi.Parameter(
            "self_name",
            openapi.IN_QUERY,
            description="Your name",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "self_company",
            openapi.IN_QUERY,
            description="Your company",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "self_address",
            openapi.IN_QUERY,
            description="Your address",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "self_city",
            openapi.IN_QUERY,
            description="Your city",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "self_county",
            openapi.IN_QUERY,
            description="Your county",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "self_country",
            openapi.IN_QUERY,
            description="Your country",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "notes",
            openapi.IN_QUERY,
            description="Additional notes",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "invoice_number",
            openapi.IN_QUERY,
            description="Invoice number",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "vat_number",
            openapi.IN_QUERY,
            description="VAT number",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "reference",
            openapi.IN_QUERY,
            description="Reference",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "sort_code",
            openapi.IN_QUERY,
            description="Sort code",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "account_number",
            openapi.IN_QUERY,
            description="Account number",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "account_holder_name",
            openapi.IN_QUERY,
            description="Account holder name",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "date_due",
            openapi.IN_QUERY,
            description="Due date of the invoice (YYYY-MM-DD format)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
        ),
        openapi.Parameter(
            "date_created",
            openapi.IN_QUERY,
            description="Creation date of the invoice (YYYY-MM-DD format)",
            type=openapi.TYPE_STRING,
            format=openapi.FORMAT_DATE,
        ),
        openapi.Parameter(
            "product_id",
            openapi.IN_QUERY,
            description="Id of a product",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "client_to",
            openapi.IN_QUERY,
            description="Id of a client",
            type=openapi.TYPE_STRING,
        ),
        TEAM_PARAMETER,
    ],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "items": openapi.Schema(
                description="The service to which the invoice relates. If product_id is used and there is no other service to add then the field can remain as '{}'.",
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "description": openapi.Schema(type=openapi.TYPE_STRING),
                        "hours": openapi.Schema(type=openapi.TYPE_INTEGER, format="decimal"),
                        "price_per_hour": openapi.Schema(type=openapi.TYPE_INTEGER, format="decimal"),
                    },
                ),
            )
        },
    ),
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
)
@api_view(["POST"])
@handle_team_context
@require_scopes(["invoices:write"])
def create_invoice_endpoint(request, team=None):
    return invoice_save(request)
