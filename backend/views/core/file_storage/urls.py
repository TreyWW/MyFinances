from django.urls import path
from django.urls.conf import include

from backend.views.core.file_storage.dashboard import file_storage_dashboard_endpoint
from backend.views.core.file_storage.upload import upload_file_endpoints

urlpatterns = [path("", file_storage_dashboard_endpoint, name="dashboard"), path("upload", upload_file_endpoints, name="upload")]

app_name = "file_storage"
