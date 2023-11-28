from django.urls import path
from . import change_name

urlpatterns = [
    path(
        "change_name",
        change_name.change_account_name,
        name="change_name",
    ),
]

app_name = "settings"
