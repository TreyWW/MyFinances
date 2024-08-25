from django.core.files.uploadedfile import TemporaryUploadedFile

from backend.utils.dataclasses import BaseServiceResponse
from backend.models import FileStorageFile, User, Organization


class CreateFileServiceResponse(BaseServiceResponse[FileStorageFile]): ...


def parse_files_for_creation(actor: User | Organization, uploaded_files: list[TemporaryUploadedFile]):
    file_objects: list[FileStorageFile] = []
    uploaded_files_count = len(uploaded_files)
    total_size_in_bytes: int = 0

    if uploaded_files_count == 0:
        return CreateFileServiceResponse(error_message="No files were uploaded.", status_code=400)

    if uploaded_files_count >= 400:
        return CreateFileServiceResponse(error_message="Too many files were uploaded. (max 400 at a time)", status_code=400)

    for file in uploaded_files:
        print(file)
        file_object = FileStorageFile(file=file, owner=actor)

        file_objects.append(file_object)
        total_size_in_bytes += file.size

    # max limit of 30gb total
    max_limit = 30 * 1024 * 1024 * 1024
    if total_size_in_bytes > max_limit:
        return CreateFileServiceResponse(error_message="Total file size exceeds the maximum limit of 30GB.", status_code=400)

    django_uploaded_files = FileStorageFile.objects.bulk_create(file_objects, batch_size=100)

    return CreateFileServiceResponse(True, response=django_uploaded_files)
