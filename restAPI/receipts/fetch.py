from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Receipt
from .serializers import ReceiptReturnedSerializer

search_param = openapi.Parameter(
    "search",
    openapi.IN_QUERY,
    description="A search string for a receipt name or date",
    type=openapi.TYPE_STRING,
    required=False,
)

user_response = openapi.Response("Receipt List", ReceiptReturnedSerializer)


@swagger_auto_schema(
    manual_parameters=[search_param],
    method="GET",
    responses={200: user_response},
)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fetch_all_receipts(request):
    search_text = request.GET.get("search")

    if search_text:
        results = (
            Receipt.objects.filter(user=request.user)
            .filter(Q(name__icontains=search_text) | Q(date__icontains=search_text))
            .order_by("-date")
        )
    else:
        results = Receipt.objects.filter(user=request.user).order_by("-date")

    serializer = ReceiptReturnedSerializer(results, many=True)
    return Response(serializer.data)
