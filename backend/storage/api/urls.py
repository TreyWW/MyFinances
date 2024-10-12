from django.urls import path
from django.views.generic import RedirectView

from .delete import recursive_file_delete_endpoint
from .fetch import fetch_table_endpoint

urlpatterns = [
    # path("delete/", recursive_file_delete_endpoint, name="delete"),
    # path("fetch/", fetch_table_endpoint, name="fetch")
    path("delete/", RedirectView.as_view(url="/dashboard"), name="delete"),
    path("fetch/", RedirectView.as_view(url="/dashboard"), name="fetch"),
]

app_name = "file_storage"
