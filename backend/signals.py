from django.core.files.storage import default_storage
from django.db.models.signals import pre_save, post_delete, post_save
from django.dispatch import receiver

from backend.models import UserSettings, Receipt, User


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
        if default_storage.exists(instance.profile_picture.name):
            instance.profile_picture.delete(save=False)


@receiver(post_delete, sender=Receipt)
def set_profile_picture_to_none(sender, instance, **kwargs):
    if instance.image:
        # Check if the file exists in the storage
        if default_storage.exists(instance.image.name):
            instance.image.delete(save=False)
            instance.image = None
            instance.save()


@receiver(post_save, sender=User)
def user_account_create_make_usersettings(sender, instance, created, **kwargs):
    print("signal ran")
    if created:
        print("signal created")
        try:
            users_settings = instance.user_profile
        except UserSettings.DoesNotExist:
            users_settings = None

        if not users_settings:
            UserSettings.objects.create(user=instance)
            print("User created from signal")
