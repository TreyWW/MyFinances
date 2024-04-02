from django.urls import path

from . import fetch, requests

urlpatterns = [
    path(
        "fetch/<str:group>/",
        fetch.fetch_all_quotas,
        name="fetch",
    ),
    path("submit_request/<slug:slug>/", requests.submit_request, name="submit_request"),
    path("request/<int:request_id>/approve/", requests.approve_request, name="approve request"),
    path("request/<int:request_id>/decline/", requests.decline_request, name="decline request"),
]

app_name = "quotas"
