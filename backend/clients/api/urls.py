from django.urls import path
from backend.clients.api import fetch, delete

urlpatterns = [
    path(
        "fetch/",
        fetch.fetch_all_clients,
        name="fetch",
    ),
    path(
        "fetch/dropdown/",
        fetch.fetch_clients_dropdown,
        name="fetch dropdown",
    ),
    path(
        "delete/<int:id>/",
        delete.client_delete,
        name="delete",
    ),
]
app_name = "clients"
