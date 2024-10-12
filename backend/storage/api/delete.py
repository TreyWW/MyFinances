from django.contrib import messages
from django.db.models import QuerySet
from django.http import HttpResponse, QueryDict
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from backend.decorators import htmx_only
from backend.models import FileStorageFile
from backend.core.types.requests import WebRequest


@require_http_methods(["DELETE"])
@htmx_only("file_storage:dashboard")
def recursive_file_delete_endpoint(request: WebRequest) -> HttpResponse:
    body_unicode = request.body.decode("utf-8")
    q = QueryDict(body_unicode, mutable=True)
    files_to_delete = q.getlist("file-checkboxes")

    all_user_files: QuerySet[FileStorageFile] = FileStorageFile.filter_by_owner(owner=request.actor)

    failed_files = []

    for file in files_to_delete:
        file_obj: FileStorageFile | None = all_user_files.filter(file_uri_path=file).first()

        if not file_obj:
            failed_files.append(file)
            continue

        file_obj.delete()

    if failed_files:
        messages.error(request, f"Failed to delete: {', '.join([file for file in failed_files])}")
        resp = render(request, "base/toast.html")
    else:
        resp = HttpResponse(status=200)

    resp["HX-Trigger"] = "reload_filestorage_table"
    return resp
