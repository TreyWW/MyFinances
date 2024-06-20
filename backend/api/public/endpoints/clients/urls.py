from django.urls import path

from . import list, delete

urlpatterns = [
    path(
        "list",
        list.list_clients_endpoint,
        name="list",
    ),
    path("delete", delete.client_delete_endpoint, name="delete"),
]

app_name = "clients"
