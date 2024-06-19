from django.db.models import Q, QuerySet

from backend.models import Client


def fetch_clients(request, *, search_text=None) -> QuerySet[Client]:
    if request.user.logged_in_as_team:
        clients = Client.objects.filter(organization=request.user.logged_in_as_team, active=True)
    else:
        clients = Client.objects.filter(user=request.user, active=True)

    if search_text:
        clients = clients.filter(Q(name__icontains=search_text) | Q(email__icontains=search_text) | Q(id__icontains=search_text))

    return clients
