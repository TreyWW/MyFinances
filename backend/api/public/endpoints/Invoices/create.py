from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from backend.api.public.decorators import require_scopes, handle_team_context
from backend.models import Client
from backend.api.public.serializers.invoices import InvoiceSerializer


@api_view(["POST"])
@handle_team_context
@require_scopes(["invoices:write"])
def create_invoice_endpoint(request, team=None):
    serializer = InvoiceSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        if "client_id" in request.data and request.data["client_id"]:
            try:
                client = Client.objects.get(user=user, id=request.data["client_id"])
                serializer.validated_data["client_to"] = client
            except Client.DoesNotExist:
                return Response({"error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

        invoice = serializer.save(user=user)
        return Response({"id": invoice.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
