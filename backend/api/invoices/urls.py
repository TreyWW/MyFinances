from django.urls import path
from .create.services import add, remove
from .create import set_destination
from . import fetch

urlpatterns = [
    path(
        "add_service/",
        add.add_service,
        name="services add",
    ),
    path(
        "remove_service/",
        remove.remove_service,
        name="services remove",
    ),
    path(
        "set_destination/to/",
        set_destination.set_destination_to,
        name="set_destination to",
    ),
    path(
        "set_destination/from/",
        set_destination.set_destination_from,
        name="set_destination from",
    ),
    path("fetch/", fetch.fetch_all_invoices, name="fetch"),
]

app_name = "invoices"
