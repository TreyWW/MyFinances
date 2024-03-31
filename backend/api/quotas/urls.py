from django.urls import path

from . import fetch, submit_request

urlpatterns = [
    path(
        "fetch/<str:group>/",
        fetch.fetch_all_quotas,
        name="fetch",
    ),
    path(
        "submit_request/<slug:slug>/",
        submit_request.submit_request,
        name="submit_request"
    )
]

app_name = "quotas"
