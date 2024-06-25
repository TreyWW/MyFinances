from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.api.public.decorators import require_scopes
from backend.api.public.types import APIRequest
from backend.models import Client
from backend.api.public.serializers.invoices import InvoiceSerializer


@api_view(["POST"])
@require_scopes(["invoices:write"])
def create_invoice_endpoint(request: APIRequest):
    serializer = InvoiceSerializer(data=request.data)
    if serializer.is_valid():
        if "client_id" in request.data and request.data["client_id"]:
            try:
                if request.team:
                    client = Client.objects.get(organization=request.team, id=request.data["client_id"])
                else:
                    client = Client.objects.get(user=request.user, id=request.data["client_id"])
                serializer.validated_data["client_to"] = client
            except Client.DoesNotExist:
                return Response({"error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

        if request.team:
            invoice = serializer.save(organization=request.team)
        else:
            invoice = serializer.save(user=requestuser)
        return Response({"id": invoice.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
