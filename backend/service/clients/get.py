from django.db.models import Q, QuerySet

from backend.models import Client, Team


def fetch_clients(request, *, search_text: str | None = None, team: Team | None = None) -> QuerySet[Client]:
    if team:
        clients = Client.objects.filter(organization=team, active=True)
    else:
        clients = Client.objects.filter(user=request.user, active=True)

    if search_text:
        clients = clients.filter(Q(name__icontains=search_text) | Q(email__icontains=search_text) | Q(id__icontains=search_text))

    return clients
