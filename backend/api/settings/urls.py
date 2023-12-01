from django.urls import path
from . import currency

urlpatterns = [
    path(
        "change_currency/",
        currency.update_currency_view,
        name="change_currency",
    ),
]

app_name = "settings"
