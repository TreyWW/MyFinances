from django.db.models.signals import pre_delete
from django.dispatch import receiver

from backend.models import FileStorageFile, MultiFileUpload, _private_storage


@receiver(pre_delete, sender=FileStorageFile)
def on_delete_remove_media_file(sender, instance: FileStorageFile, **kwargs):
    # Check if the file exists in the storage
    if instance.file and _private_storage().exists(instance.file.name):
        instance.file.delete(save=False)
        instance.file = None
        instance.save()
