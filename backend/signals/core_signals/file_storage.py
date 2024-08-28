import logging

from django.db.models.signals import pre_delete, post_save
from django.dispatch import receiver

from backend.models import FileStorageFile, MultiFileUpload, _private_storage, StorageUsage, PlanFeature

logger = logging.getLogger(__name__)


@receiver(pre_delete, sender=FileStorageFile)
def on_delete_remove_media_file(sender, instance: FileStorageFile, **kwargs):
    # Check if the file exists in the storage
    if instance.file and _private_storage().exists(instance.file.name):
        instance.file.delete(save=False)
        instance.file = None
        instance.save()

    existing_usage = instance.find_existing_usage("storage")

    if existing_usage:
        existing_usage.end_now().save()


@receiver(post_save, sender=FileStorageFile)
def on_file_creation(sender, instance: FileStorageFile, created, **kwargs):
    if not created:
        return

    StorageUsage.objects.create(
        owner=instance.owner,
        feature=PlanFeature.objects.get(slug="storage"),
        start_time=instance.created_at,
        file_uri_path=instance.file_uri_path,
        size_in_MB=instance.file.size / 1024 / 1024,
    )


# On update file
@receiver(post_save, sender=FileStorageFile)
def on_update_file(sender, instance: FileStorageFile, created, **kwargs):
    if created:
        return

    if hasattr(instance, "__original_file") and instance.file != instance.__original_file:
        if hasattr(instance, "__original_file_uri_path") and instance.__original_file_uri_path:
            existing_usage = instance.find_existing_usage("storage", instance.__original_file_uri_path)
        else:
            existing_usage = instance.find_existing_usage("storage")

        if existing_usage:
            existing_usage.end_now().save(update_fields=["end_time"])

            StorageUsage.objects.create(
                owner=instance.owner,
                feature="file-storage",
                start_at=instance.updated_at,
                file=instance.file,
                file_uri_path=instance.file_uri_path,
                size_in_MB=instance.file.size / 1024 / 1024,
            )
        else:
            logger.error("Could not find existing usage for file storage")
