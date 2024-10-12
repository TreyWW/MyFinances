from django.utils.html import escape
from django.views.decorators.http import require_GET

from backend.decorators import htmx_only
from backend.models import FileStorageFile

# from backend.core.service.billing.calculate.test import generate_monthly_billing_summary
from backend.core.service.file_storage.utils import format_file_size
from backend.core.types.requests import WebRequest

from django.shortcuts import render


@require_GET
@htmx_only("file_storage:dashboard")
def fetch_table_endpoint(request: WebRequest):
    path = request.GET.get("path", "")

    files = FileStorageFile.filter_by_owner(request.actor).filter(file_uri_path__startswith=path).order_by("file_uri_path")

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

    return render(request, "pages/file_storage/_table_body.html", {"files": files_with_names, "directory": escape(path)})
