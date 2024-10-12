from django.urls import path
from . import generate, fetch

urlpatterns = [
    path(
        "generate/",
        generate.generate_report_endpoint,
        name="generate",
    ),
    path("fetch/", fetch.fetch_reports_endpoint, name="fetch"),
]

app_name = "reports"
