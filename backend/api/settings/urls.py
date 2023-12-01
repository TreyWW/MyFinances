from django.urls import path

from . import currency, change_name

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
]

app_name = "settings"
