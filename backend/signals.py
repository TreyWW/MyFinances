from backend.models import UserSettings
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from django.core.files.storage import default_storage


@receiver(pre_save, sender=UserSettings)
def delete_old_profile_picture(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_profile = UserSettings.objects.get(pk=instance.pk)
    except UserSettings.DoesNotExist:
        return

    if (
        old_profile.profile_picture
        and old_profile.profile_picture != instance.profile_picture
    ):
        # If the profile picture has been updated, delete the old file
        old_profile.profile_picture.delete(save=False)


@receiver(post_delete, sender=UserSettings)
def set_profile_picture_to_none(sender, instance, **kwargs):
    if instance.profile_picture:
        # Check if the file exists in the storage
        if not default_storage.exists(instance.profile_picture.name):
            instance.profile_picture = None
            instance.save()
