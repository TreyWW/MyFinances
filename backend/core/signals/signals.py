from __future__ import annotations

from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient

cache: RedisCacheClient = cache
from django.core.files.storage import default_storage
from django.db.models.signals import pre_save, post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

import settings.settings
from backend.models import UserSettings, Receipt, User, FeatureFlags, VerificationCodes
from settings.helpers import send_email


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
    # Check if the file exists in the storage
    if instance.profile_picture and default_storage.exists(instance.profile_picture.name):
        instance.profile_picture.delete(save=False)


@receiver(pre_delete, sender=Receipt)
def delete_old_receipts(sender, instance, **kwargs):
    # Check if the file exists in the storage
    if instance.image and default_storage.exists(instance.image.name):
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


@receiver(post_save, sender=FeatureFlags)
def refresh_feature_cache(sender, instance: FeatureFlags, **kwargs):
    feature = instance.name
    key = f"myfinances:feature_flag:{feature}"

    cached_value = cache.get(key)

    if cached_value:
        return cache.delete(key)


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance: User, created, **kwargs):
    if created:
        email_message = f"""
            Welcome to MyFinances{f", {instance.first_name}" if instance.first_name else ""}!

            We're happy to have you join us. We are still in development and working on the core features.

            In app we have a live chat, so please drop us a message or email support@myfinances.cloud if you have any queries.

            Thank you for using MyFinances!
        """
        magic_link = VerificationCodes.objects.create(user=instance, service="create_account")
        token_plain = magic_link.token
        magic_link.hash_token()
        magic_link_url = settings.settings.SITE_URL + reverse(
            "auth:login create_account verify", kwargs={"uuid": magic_link.uuid, "token": token_plain}
        )
        email_message += f"""
            To start with, you must first **verify this email** so that we can link your account to this email.
            Click the link below to activate your account, no details are required, once pressed you're all set!

            Verify Link: {magic_link_url}
        """

        email = send_email(destination=instance.email, subject="Welcome to MyFinances", content=email_message)

        #     User.send_welcome_email(instance)
