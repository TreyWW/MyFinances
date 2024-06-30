from django.urls import path

from . import list, delete
from .create import client_create_endpoint

urlpatterns = [
    path(
        "",
        list.list_clients_endpoint,
        name="list",
    ),
    path("<int:id>/", delete.client_delete_endpoint, name="delete"),
    path("create/", client_create_endpoint, name="create"),
]

app_name = "clients"
