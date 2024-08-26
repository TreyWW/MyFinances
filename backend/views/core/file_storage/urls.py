from django.urls import path
from django.urls.conf import include

from backend.views.core.file_storage.dashboard import file_storage_dashboard_endpoint
from backend.views.core.file_storage.upload import (
    upload_file_dashboard_endpoints,
    upload_file_via_batch_endpoint,
    end_file_upload_batch_endpoint,
    start_file_upload_batch_endpoint,
)

upload_paths = [
    path("", upload_file_dashboard_endpoints, name="dashboard"),
    path("start_batch/", start_file_upload_batch_endpoint, name="start_batch"),
    path("end_batch/", end_file_upload_batch_endpoint, name="end_batch"),
    path("add_to_batch/", upload_file_via_batch_endpoint, name="add_to_batch"),
]

urlpatterns = [
    path("", file_storage_dashboard_endpoint, name="dashboard"),
    path("upload/", include((upload_paths, "upload"), namespace="upload")),
]

app_name = "file_storage"
