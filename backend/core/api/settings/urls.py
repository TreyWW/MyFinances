from django.urls import path

from . import change_name, profile_picture, preferences
from .api_keys import generate_api_key_endpoint, revoke_api_key_endpoint
from .defaults import handle_client_defaults_endpoints, remove_client_default_logo_endpoint
from .email_templates import save_email_template

urlpatterns = [
    path(
        "account_preferences/",
        preferences.update_account_preferences,
        name="account_preferences",
    ),
    path(
        "change_name/",
        change_name.change_account_name,
        name="change_name",
    ),
    path("profile_picture/", profile_picture.change_profile_picture_endpoint, name="update profile picture"),
    path("api_keys/generate/", generate_api_key_endpoint, name="api_keys generate"),
    path("api_keys/revoke/<str:key_id>/", revoke_api_key_endpoint, name="api_keys revoke"),
    path("client_defaults/<int:client_id>/", handle_client_defaults_endpoints, name="client_defaults"),
    path("client_defaults/", handle_client_defaults_endpoints, name="client_defaults without client"),
    path("client_defaults/remove_default_logo/", remove_client_default_logo_endpoint, name="client_defaults remove logo without client"),
    path("client_defaults/remove_default_logo/<int:client_id>", remove_client_default_logo_endpoint, name="client_defaults remove logo"),
    path("email_templates/<str:template>/save/", save_email_template, name="email_template save"),
]

app_name = "settings"
