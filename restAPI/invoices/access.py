from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Invoice, InvoiceURL
from .serializers import InvoiceURLCreatedSerializer

user_response = openapi.Response("URL", InvoiceURLCreatedSerializer)

@swagger_auto_schema(
    method="POST",
    responses={200: user_response},
)
@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def create_code(request, invoice_id: Invoice.id):
    try:
        invoice = Invoice.objects.get(id=invoice_id)
    except Invoice.DoesNotExist:
        return Response({"detail": "Invoice not found"}, status=status.HTTP_404_NOT_FOUND)

    if not request.user or request.user != invoice.user:
        return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

    code = InvoiceURL.objects.create(invoice=invoice, created_by=request.user)

    response_data = {
        "success": True,
        "id": invoice_id,
        # "url": code.,
        "uuid": code.uuid,
    }

    serializer = InvoiceURLCreatedSerializer(response_data)
    return Response(serializer.data)
