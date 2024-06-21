from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from backend.service.invoices.create.services.add import add
from backend.api.public.serializers.invoices import InvoiceProductSerializer


@api_view(["POST"])
def add_service_endpoint(request):
    serializer = InvoiceProductSerializer(data=request.data)
    if serializer.is_valid():
        return Response(add(request), status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
