from django.urls import path, include

from .dashboard import dashboard
from .settings import view_settings_page_endpoint, edit_form_endpoint, create_form_endpoint, form_builder_list_forms_endpoint

FORM_BUILDER_URLS = [
    path("", form_builder_list_forms_endpoint, name="dashboard"),  # needs view
    path("<uuid:form_uuid>/edit/", edit_form_endpoint, name="edit"),
    path("create/", create_form_endpoint, name="create"),
]

urlpatterns = [
    path("", dashboard, name="dashboard"),
    path("settings/", view_settings_page_endpoint, name="settings"),
    path("settings/<str:page>/", view_settings_page_endpoint, name="settings with page"),
    # path("settings/<str:page>/<str:sub_page>", view_settings_page_endpoint, name="settings with page and subpage"),
    path("form-builder/", include((FORM_BUILDER_URLS, "form_builder"), namespace="form_builder")),
]

app_name = "onboarding"
