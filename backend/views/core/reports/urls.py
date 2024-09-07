from django.urls import path

from .dashboard import view_reports_endpoint

urlpatterns = [
    path("", view_reports_endpoint, name="dashboard"),
]

app_name = "reports"
