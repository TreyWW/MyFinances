from django.db.models import Case, When, CharField
from django.db.models.expressions import Value, F
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.core.api.public.decorators import require_scopes
from backend.core.api.public.helpers.response import APIResponse
from backend.core.api.public.serializers.invoices import InvoiceSerializer
from backend.core.api.public.swagger_ui import TEAM_PARAMETER
from backend.core.api.public.types import APIRequest

from backend.finance.models import Invoice
from backend.core.service.invoices.common.fetch import get_context


@swagger_auto_schema(
    method="get",
    operation_description="List all invoices",
    operation_id="list_invoices",
    manual_parameters=[
        TEAM_PARAMETER,
        # openapi.Parameter(
        #     "sort",
        #     openapi.IN_QUERY,
        #     description="Field you want to order by to. Sort options: 'date_due', 'id', 'status'. Default by 'id'.",
        #     type=openapi.TYPE_STRING,
        # ),
        # openapi.Parameter(
        #     "sort_direction",
        #     openapi.IN_QUERY,
        #     description="Order by descending or ascending. 'False' for descending and 'True' for ascending. Default is ascending.",
        #     type=openapi.TYPE_STRING,
        # ),
        # openapi.Parameter(
        #     "filter_type",
        #     openapi.IN_QUERY,
        #     description="Select filter type by which results will be filtered. Filter types are 'status' and "
        #                 "'amount'. By default there is no filter types applied.",
        #     type=openapi.TYPE_STRING,
        # ),
        # openapi.Parameter(
        #     "filter",
        #     openapi.IN_QUERY,
        #     description="Select filter by which results will be filtered. Filters for 'status' are 'paid', "
        #                 "'pending', 'overdue', 'draft' and for 'amount' are '20+', '50+', '100+'. By default there is no "
        #                 "filter applied.",
        #     type=openapi.TYPE_STRING,
        # ),
    ],
    responses={
        200: openapi.Response(
            description="List of invoices",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    "invoices": openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT)),
                },
            ),
        )
    },
)
@api_view(["GET"])
@require_scopes(["invoices:read"])
def list_invoices_endpoint(request: APIRequest) -> Response:
    if request.team:
        invoices = Invoice.objects.filter(organization=request.team)
    else:
        invoices = Invoice.objects.filter(user=request.user)

    # sort_by = request.query_params.get("sort")
    # sort_direction = request.query_params.get("sort_direction", "")
    # action_filter_type = request.query_params.get("filter_type")
    # action_filter_by = request.query_params.get("filter")

    # todo: add back sort + filters on backend for API

    _, invoices = get_context(invoices)  # type: ignore[assignment]

    serializer = InvoiceSerializer(invoices, many=True)

    return APIResponse(True, {"invoices": serializer.data}, status=status.HTTP_200_OK)
