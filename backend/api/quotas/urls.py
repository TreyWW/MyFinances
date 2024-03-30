from django.urls import path

from . import fetch

urlpatterns = [
    path(
        "fetch/<str:group>/",
        fetch.fetch_all_quotas,
        name="fetch",
    )
]

app_name = "quotas"
