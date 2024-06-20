from django.urls import path

from . import add, create


urlpatterns = [
    path(
        "add_service",
        add.add_service_endpoint,
        name="services add",
    ),
    path(
        "create",
        create.create_invoice_endpoint,
        name="create",
    ),
]

app_name = "invoices"
