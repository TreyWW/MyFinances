from django.urls import path

from . import fetch

urlpatterns = [
    path("fetch/", fetch.fetch_products, name="fetch"),
]

app_name = "products"
