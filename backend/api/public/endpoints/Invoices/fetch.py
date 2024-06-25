from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.api.public.decorators import require_scopes
from backend.api.public.serializers.invoices import InvoiceSerializer
from backend.api.public.swagger_ui import TEAM_PARAMETER
from backend.api.public.types import APIRequest
from backend.models import Invoice
from backend.service.invoices.fetch import get_context


@swagger_auto_schema(
    method="get",
    operation_description="Fetch all invoices",
    operation_id="invoices_list",
    manual_parameters=[
        TEAM_PARAMETER,
        openapi.Parameter(
            "sort",
            openapi.IN_QUERY,
            description="Field you want to order by to. Sort options: 'date_due', 'id', 'payment_status'. Default by " "'id'.",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "sort_direction",
            openapi.IN_QUERY,
            description="Order by descending or ascending. False for descending and True for ascending. Default is " "ascending.",
            type=openapi.TYPE_BOOLEAN,
        ),
        openapi.Parameter(
            "filter_type",
            openapi.IN_QUERY,
            description="Select filter type by which results will be filtered. Filter types are 'payment_status' and "
            "'amount'. By default there is no filter types applied.",
            type=openapi.TYPE_STRING,
        ),
        openapi.Parameter(
            "filter",
            openapi.IN_QUERY,
            description="Select filter by which results will be filtered. Filters for 'payment_status' are 'paid', "
            "'pending', 'overdue' and for 'amount' are '20+', '50+', '100+'. By default there is no "
            "filter applied.",
            type=openapi.TYPE_STRING,
        ),
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
def fetch_all_invoices_endpoint(request: APIRequest):
    if request.user.is_authenticated:
        if hasattr(request.user, "logged_in_as_team"):
            invoices = Invoice.objects.filter(organization=request.user.logged_in_as_team)
        else:
            invoices = Invoice.objects.filter(user=request.user)
    else:
        invoices = Invoice.objects.none()

    sort_by = request.data.get("sort")
    sort_direction = request.data.get("sort_direction", "")
    action_filter_type = request.data.get("filter_type")
    action_filter_by = request.data.get("filter")

    # TODO: Decide on how to handle this part or to get rid of it in API
    previous_filters = {
        "payment_status": {
            "paid": True if request.data.get("payment_status_paid") else False,
            "pending": True if request.data.get("payment_status_pending") else False,
            "overdue": True if request.data.get("payment_status_overdue") else False,
        },
        "amount": {
            "20+": True if request.data.get("amount_20+") else False,
            "50+": True if request.data.get("amount_50+") else False,
            "100+": True if request.data.get("amount_100+") else False,
        },
    }

    _, invoices = get_context(invoices, sort_by, sort_direction, action_filter_type, action_filter_by, previous_filters)

    serializer = InvoiceSerializer(invoices, many=True)

    return Response({"success": True, "invoices": serializer.data}, status=status.HTTP_200_OK)
