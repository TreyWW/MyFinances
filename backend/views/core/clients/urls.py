from django.urls import path

from .dashboard import clients_dashboard_endpoint
from .detail import client_detail_endpoint, delete_client_endpoint
from .create import create_client_endpoint

urlpatterns = [
    path("", clients_dashboard_endpoint, name="dashboard"),
    path("<int:id>/", client_detail_endpoint, name="detail"),
    path(
        "create/",
        create_client_endpoint,
        name="create",
    ),
    path("<int:id>/delete/", delete_client_endpoint, name="delete"),
    # path("<int:id>/edit/", client_edit_endpoint, name="edit"),
]

app_name = "clients"
