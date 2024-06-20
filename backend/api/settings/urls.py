from django.urls import path

from . import currency, change_name, profile_picture

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
]

app_name = "settings"
