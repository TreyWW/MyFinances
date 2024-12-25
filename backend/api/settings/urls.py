from django.urls import path

from .defaults import handle_client_defaults_endpoints, remove_client_default_logo_endpoint
from .email_templates import save_email_template

urlpatterns = [
    path("client_defaults/<int:client_id>/", handle_client_defaults_endpoints, name="client_defaults"),
    path("client_defaults/", handle_client_defaults_endpoints, name="client_defaults without client"),
    path("client_defaults/remove_default_logo/", remove_client_default_logo_endpoint, name="client_defaults remove logo without client"),
    path("client_defaults/remove_default_logo/<int:client_id>", remove_client_default_logo_endpoint, name="client_defaults remove logo"),
    path("email_templates/<str:template>/save/", save_email_template, name="email_template save"),
]

app_name = "settings"
