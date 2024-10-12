from django.core.files.uploadedfile import UploadedFile

from backend.core.utils.dataclasses import BaseServiceResponse
from backend.models import FileStorageFile, User, Organization


class CreateFileServiceResponse(BaseServiceResponse[list[FileStorageFile]]): ...


def parse_files_for_creation(actor: User | Organization, uploaded_files: list[UploadedFile]):
    file_objects: list[FileStorageFile] = []
    uploaded_files_count = len(uploaded_files)
    total_size_in_bytes: int = 0

    if uploaded_files_count == 0:
        return CreateFileServiceResponse(error_message="No files were uploaded.", status_code=400)

    if uploaded_files_count >= 400:
        return CreateFileServiceResponse(error_message="Too many files were uploaded. (max 400 at a time)", status_code=400)

    for file in uploaded_files:
        file_object = FileStorageFile(file=file, owner=actor)  # type: ignore[misc]

        file_objects.append(file_object)
        total_size_in_bytes += file.size or 0

    # max limit of 30gb total
    max_limit = 30 * 1024 * 1024 * 1024
    if total_size_in_bytes > max_limit:
        return CreateFileServiceResponse(error_message="Total file size exceeds the maximum limit of 30GB.", status_code=400)

    # Todo: WARNING - bulk create bypasses signals so this will need to be changed when we add usage based pricing for this

    django_uploaded_files = FileStorageFile.objects.bulk_create(file_objects, batch_size=100)

    return CreateFileServiceResponse(True, response=django_uploaded_files)
