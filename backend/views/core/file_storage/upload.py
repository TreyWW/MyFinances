from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from backend.types.requests import WebRequest
from backend.models import FileStorageFile

from backend.service.file_storage.create import parse_files_for_creation

from django.urls import reverse


def upload_file_post(request: WebRequest):
    django_bulk_files: list[FileStorageFile]

    files = request.FILES.getlist("files")  # Retrieve all uploaded files
    should_override = request.POST.get("should_override", False)

    service_response = parse_files_for_creation(request.actor, files)

    if service_response.success:
        messages.success(request, f"Successfully uploaded {len(files)} files")
        if request.htmx:
            resp = HttpResponse()
            resp["HX-Location"] = reverse("file_storage:dashboard")
            return resp
        return redirect("file_storage:dashboard")

    messages.error(request, service_response.error or "Something went wrong")
    if request.htmx:
        resp = HttpResponse()
        resp["HX-Location"] = reverse("file_storage:upload")
        return resp
    return redirect("file_storage:upload")


def upload_file_dashboard(request: WebRequest):
    return render(request, "pages/file_storage/upload.html")


@require_http_methods(["POST", "GET"])
def upload_file_endpoints(request: WebRequest) -> HttpResponse:
    if request.method == "POST":
        return upload_file_post(request)
    return upload_file_dashboard(request)
