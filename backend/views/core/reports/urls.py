from django.urls import path

from .dashboard import view_reports_endpoint
from .view import view_report_endpoint

urlpatterns = [
    path("", view_reports_endpoint, name="dashboard"),
    path("view/<uuid:uuid>", view_report_endpoint, name="view"),
]

app_name = "reports"
