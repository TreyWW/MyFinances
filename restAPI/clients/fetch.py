from django.db.models import Q
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from backend.models import Client
from restAPI.serializers import ClientSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def fetch_all_clients(request):
    search_text = request.GET.get("search")

    clients = Client.objects.filter(user=request.user, active=True)

    if search_text:
        clients = clients.filter(
            Q(name__icontains=search_text)
            | Q(email__icontains=search_text)
            | Q(id__icontains=search_text)
        )

    serializer = ClientSerializer(clients, many=True)
    return Response(serializer.data)
