from django.db.models import QuerySet
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.api.public.authentication import BearerAuthentication
from backend.api.public.serializers.clients import ClientSerializer
from backend.models import Client
from backend.service.clients.get import fetch_clients


@api_view(["GET"])
@authentication_classes([BearerAuthentication])
@permission_classes([IsAuthenticated])
def list_clients_endpoint(request):
    search_text = request.GET.get("search")

    clients: QuerySet[Client] = fetch_clients(request, search_text=search_text)

    serializer = ClientSerializer(clients, many=True)

    return Response({"success": True, "clients": serializer.data})
