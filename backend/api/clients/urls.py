from django.urls import path
from . import fetch

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
]

app_name = "clients"
