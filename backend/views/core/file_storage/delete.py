from django.http import HttpResponse, QueryDict, JsonResponse
from django.views.decorators.http import require_http_methods

from backend.models import FileStorageFile
from backend.types.requests import WebRequest


@require_http_methods(["DELETE"])
def recursive_file_delete_endpoint(request: WebRequest) -> HttpResponse:
    body_unicode = request.body.decode("utf-8")
    q = QueryDict(body_unicode, mutable=True)
    files_to_delete = q.getlist("file-checkboxes")
    for file in files_to_delete:
        # Now to delete, Here I need some help
        ...
    return JsonResponse({"status": "success"})
