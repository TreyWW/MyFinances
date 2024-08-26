from django.urls import path
from django.urls.conf import include

from .dashboard import billing_dashboard_endpoint
from backend.views.core.file_storage.upload import (
    upload_file_dashboard_endpoints,
)

upload_paths = [
    path("", upload_file_dashboard_endpoints, name="dashboard"),
]

urlpatterns = [
    path("", billing_dashboard_endpoint, name="dashboard"),
    path("upload/", include((upload_paths, "upload"), namespace="upload")),
]

app_name = "billing"
