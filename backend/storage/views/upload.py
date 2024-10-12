import json
import os
from django.contrib import messages
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from backend.core.types.requests import WebRequest
from backend.models import FileStorageFile, MultiFileUpload
from backend.core.models import _private_storage, upload_to_user_separate_folder

from backend.core.service.file_storage.create import parse_files_for_creation

from django.urls import reverse


def upload_file_post(request: WebRequest):
    django_bulk_files: list[FileStorageFile]

    files = request.FILES.getlist("files")  # Retrieve all uploaded files
    print(files)
    for file in files:
        print(type(file))
        print(file.name)

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
        resp["HX-Location"] = reverse("file_storage:upload:dashboard")
        return resp
    return redirect("file_storage:upload:dashboard")


@require_http_methods(["POST"])
def start_file_upload_batch_endpoint(request: WebRequest):
    batch = MultiFileUpload.objects.create(user=request.user)

    return JsonResponse({"batch": batch.uuid})


@require_http_methods(["POST"])
def end_file_upload_batch_endpoint(request):
    try:
        # Decode and load JSON data from request body
        body_unicode = request.body.decode("utf-8")
        body_data = json.loads(body_unicode)

        batch = body_data.get("batch")

        batch_obj = MultiFileUpload.objects.filter(uuid=batch, user=request.user).first()

        if not batch_obj:
            return JsonResponse({"error": "Batch not found"}, status=404)

        batch_obj.finished_at = timezone.now()
        batch_obj.save()

        return JsonResponse({"success": True})

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)


@require_http_methods(["POST"])
def upload_file_via_batch_endpoint(request: WebRequest):
    batch = request.POST.get("batch", "")

    batch_obj = MultiFileUpload.objects.filter(uuid=batch, user=request.user).first()

    if not batch_obj:
        return JsonResponse({"error": "Batch not found"}, status=404)

    if batch_obj.is_finished():
        return JsonResponse({"error": "Batch already finished"}, status=400)

    file: UploadedFile | None = request.FILES.get("file")
    file_dir: str = request.POST.get("file_dir", "")

    if not file:
        return JsonResponse({"error": "File not found"}, status=404)

    if not file.name:
        return JsonResponse({"error": "File name not found"}, status=400)

    if file_dir:
        relative_path = os.path.join(file_dir, file.name)
        full_file_path = upload_to_user_separate_folder(FileStorageFile, relative_path, optional_actor=request.actor)
    else:
        relative_path = file.name
        full_file_path = upload_to_user_separate_folder(FileStorageFile, relative_path, optional_actor=request.actor)

    existing_file_under_path: FileStorageFile | None = (
        FileStorageFile.filter_by_owner(request.actor).filter(file_uri_path=relative_path).first()
    )

    if existing_file_under_path:
        # existing_usage = existing_file_under_path.find_existing_usage("storage")
        # if existing_usage:
        #     existing_usage.end_now().save(update_fields=["end_at"])
        _private_storage().delete(full_file_path)  # WILL OVERRIDE IT RATHER THAN USE NEW NAME
        existing_file_under_path.delete()
        # todo add an option to not override

    saved_path = _private_storage().save(full_file_path, ContentFile(file.read()))

    saved_file = FileStorageFile.objects.create(file=saved_path, owner=request.actor, file_uri_path=relative_path)

    batch_obj.files.add(saved_file)
    return JsonResponse({"success": True})


@require_http_methods(["POST", "GET"])
def upload_file_dashboard_endpoints(request: WebRequest) -> HttpResponse:
    return render(request, "pages/file_storage/upload.html")
