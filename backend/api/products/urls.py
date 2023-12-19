from django.urls import path

from . import fetch, create

urlpatterns = [
    path("fetch/", fetch.fetch_products, name="fetch"),
    path("create/", create.create_product, name="create"),
]

app_name = "products"
