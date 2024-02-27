from django.urls import path
from . import fetch, delete

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
        "delete/<int:client_id>/",
        delete.delete_client,
        name="delete",
    ),
    # path("invite/<int:client_id>/", invite.invite_client, name="invite"),
]

app_name = "clients"
