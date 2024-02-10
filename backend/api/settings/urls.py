from django.urls import path

from . import currency, change_name, privacy_settings

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
    path(
        "toggle/privacy/allow_receipt_parsing/",
        privacy_settings.allow_receipt_parsing,
        name="allow_receipt_parsing",
    ),
]

app_name = "settings"
