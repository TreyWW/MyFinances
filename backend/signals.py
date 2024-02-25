from django.core.files.storage import default_storage
from django.db.models.signals import pre_save, post_delete, post_save, post_migrate
from django.dispatch import receiver

from backend.models import UserSettings, Receipt, User, FeatureFlags


@receiver(pre_save, sender=UserSettings)
def delete_old_profile_picture(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_profile = UserSettings.objects.get(pk=instance.pk)
    except UserSettings.DoesNotExist:
        return

    if old_profile.profile_picture and old_profile.profile_picture != instance.profile_picture:
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
    if created:
        try:
            users_settings = instance.user_profile
        except UserSettings.DoesNotExist:
            users_settings = None

        if not users_settings:
            UserSettings.objects.create(user=instance)


@receiver(post_delete, sender=Receipt)
def delete_receipt_image_on_delete(sender, instance: Receipt, **kwargs):
    instance.image.delete(False)


feature_flags = [{"name": "areSignupsEnabled", "default": True, "pk": 1}]


def insert_initial_data(**kwargs):
    for feature in feature_flags:
        FeatureFlags.objects.get_or_create(
            id=feature.get("pk"),
            name=feature.get("name"),
            value=feature.get("default"),
        )


post_migrate.connect(insert_initial_data)
