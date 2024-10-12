from django.urls import path

from . import healthcheck

urlpatterns = [
    path(
        "ping/",
        healthcheck.ping,
        name="ping",
    ),
    path(
        "healthcheck/",
        healthcheck.healthcheck,
        name="healthcheck",
    ),
]

app_name = "healthcheck"
