from django.contrib import admin

from django.urls import include, path

from .edit_form import edit_form_name_endpoint
from .inputs import new_input_endpoint, save_field_endpoint, edit_fields_order, delete_field_endpoint

form_fields = [
    path("<uuid:field_uuid>/save/", save_field_endpoint, name="save"),
    path("<uuid:field_uuid>/delete/", delete_field_endpoint, name="delete"),
    path("new/", new_input_endpoint, name="new"),
    path("order/", edit_fields_order, name="order"),
]

forms = [
    path("<uuid:form_uuid>/change_name/", edit_form_name_endpoint, name="edit_form_name"),
    path("<uuid:form_uuid>/inputs/", include((form_fields, "inputs"), namespace="inputs")),
]

urlpatterns = [
    path("forms/", include((forms, "form_builder"), namespace="form_builder")),
]

app_name = "onboarding"
