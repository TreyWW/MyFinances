from django.contrib import admin

from django.urls import include, path

from .edit_form import edit_form_name_endpoint

forms = [
    path("<uuid:form_uuid>/change_name/", edit_form_name_endpoint, name="edit_form_name"),
]

urlpatterns = [
    path("forms/", include((forms, "form_builder"), namespace="form_builder")),
]

app_name = "onboarding"
