from django.db.models import Q, QuerySet

from backend.models import Client, Organization
from backend.core.utils.dataclasses import BaseServiceResponse


class FetchClientServiceResponse(BaseServiceResponse[QuerySet[Client]]): ...


def fetch_clients(request, *, search_text: str | None = None, team: Organization | None = None) -> FetchClientServiceResponse:
    if team:
        clients = Client.objects.filter(organization=team, active=True)
    else:
        clients = Client.objects.filter(user=request.user, active=True)

    if search_text:
        clients = clients.filter(Q(name__icontains=search_text) | Q(email__icontains=search_text) | Q(id__icontains=search_text))

    return FetchClientServiceResponse(True, clients)
