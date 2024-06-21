from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from backend.api.public.decorators import handle_team_context, require_scopes
from backend.service.invoices.create.services.add import add
from backend.api.public.serializers.invoices import InvoiceProductSerializer


@api_view(["POST"])
@handle_team_context
@require_scopes(["invoices:write"])
def add_service_endpoint(request, team=None):
    serializer = InvoiceProductSerializer(data=request.data)
    if serializer.is_valid():
        return Response(add(request), status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
