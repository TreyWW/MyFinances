from django.shortcuts import render
from django.utils.html import escape

from backend.core.models import FileStorageFile
from backend.core.service.file_storage.utils import format_file_size
from backend.core.types.requests import WebRequest


def file_storage_dashboard_endpoint(request: WebRequest):
    directory = request.GET.get("dir", "")

    files = FileStorageFile.objects.filter(file__startswith=directory).order_by("file")

    files_with_names = [
        {
            "name": file.file.name.split("/")[-1],
            "url": file.file.url,
            "file_uri_path": file.file_uri_path,
            "size": format_file_size(file.file.size),
            "last_modified": file.updated_at,
        }
        for file in files
    ]

    return render(request, "pages/file_storage/dashboard.html", {"files": files_with_names, "directory": escape(directory)})
