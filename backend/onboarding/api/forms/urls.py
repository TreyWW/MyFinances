from django.urls import path

from .list import list_forms_endpoint
from .delete import delete_form_endpoint
from .create import create_form_endpoint

urlpatterns = [
    path("list/", list_forms_endpoint, name="list"),
    path("create/", create_form_endpoint, name="create"),
    path("<uuid:uuid>/delete/", delete_form_endpoint, name="delete"),
]

app_name = "forms"
