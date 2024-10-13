from django.urls import path

from .list import list_forms_endpoint
from .edit import edit_form_endpoint

urlpatterns = [
    path("", list_forms_endpoint, name="list"),
    path("<uuid:uuid>/", edit_form_endpoint, name="edit"),
]

app_name = "forms"
