from django.urls import path
from .view import view_all

urlpatterns = [
    path(
        "fetch",
        view_all.fetch_all_clients,
        name="fetch",
    ),
]

app_name = "clients"
