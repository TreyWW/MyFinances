from __future__ import annotations
from uuid import uuid4
from django.db import models
from backend.models import OwnerBase, _private_storage, upload_to_user_separate_folder, User


class FileStorageFile(OwnerBase):
    file = models.FileField(upload_to=upload_to_user_separate_folder, storage=_private_storage)
    file_uri_path = models.CharField(max_length=500)  # relative path not including user folder/media
    last_edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, editable=False, related_name="files_edited")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    __original_file = None
    __original_file_uri_path = None

    def __init__(self, *args, **kwargs):
        super(FileStorageFile, self).__init__(*args, **kwargs)
        self.__original_file = self.file
        self.__original_file_uri_path = self.file_uri_path


class MultiFileUpload(OwnerBase):
    files = models.ManyToManyField(FileStorageFile, related_name="multi_file_uploads")
    started_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True, editable=False)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    def is_finished(self):
        return self.finished_at is not None
