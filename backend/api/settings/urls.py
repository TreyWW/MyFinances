from django.urls import path

from . import currency, change_name, profile_picture
from .api_keys import generate_api_key_endpoint, revoke_api_key_endpoint

urlpatterns = [
    path(
        "change_currency/",
        currency.update_currency_view,
        name="change_currency",
    ),
    path(
        "change_name/",
        change_name.change_account_name,
        name="change_name",
    ),
    path("profile_picture/", profile_picture.change_profile_picture_endpoint, name="update profile picture"),
    path("api_keys/generate/", generate_api_key_endpoint, name="api_keys generate"),
    path("api_keys/revoke/<str:key_id>/", revoke_api_key_endpoint, name="api_keys revoke"),
]

app_name = "settings"
