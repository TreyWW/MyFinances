from django.urls import path

from . import convert

urlpatterns = [
    path(
        "convert/",
        convert.currency_conversion,
        name="convert",
    ),
]

app_name = "currency_converter"
