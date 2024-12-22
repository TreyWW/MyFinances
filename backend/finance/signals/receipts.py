from django.core.files.storage import default_storage
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from backend.finance.models import Receipt


@receiver(pre_delete, sender=Receipt)
def delete_old_receipts(sender, instance, **kwargs):
    # Check if the file exists in the storage
    if instance.image and default_storage.exists(instance.image.name):
        instance.image.delete(save=False)
        instance.image = None
        instance.save()
