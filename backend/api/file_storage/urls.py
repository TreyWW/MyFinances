from django.urls import path

from .delete import recursive_file_delete_endpoint
from .fetch import fetch_table_endpoint

urlpatterns = [path("delete/", recursive_file_delete_endpoint, name="delete"), path("fetch/", fetch_table_endpoint, name="fetch")]

app_name = "file_storage"
