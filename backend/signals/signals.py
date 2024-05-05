from __future__ import annotations

from django.core.cache import cache
from django.core.cache.backends.redis import RedisCacheClient

from backend.types.emails import SingleEmailInput

cache: RedisCacheClient = cache
from django.core.files.storage import default_storage
from django.db.models.signals import pre_save, post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.urls import reverse

import settings.settings
from backend.models import UserSettings, Receipt, User, FeatureFlags, VerificationCodes
from settings.helpers import ARE_EMAILS_ENABLED, send_email


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


@receiver(post_delete, sender=Receipt)
def delete_receipt_image_on_delete(sender, instance: Receipt, **kwargs):
    instance.image.delete(False)


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

            We're happy to have you join us. We are still in development and are still working on the core mechanics.
            If you find any bugs with our software, create a bug report on our
            Github Issues (https://github.com/TreyWW/MyFinances/issues/new?assignees=&labels=bug&projects=&template=bug-report.md&title=%5BBUG%5D+)
            and we'll try to help debug the issue or squash the bug.

            Thank you for using MyFinances.
        """
        if ARE_EMAILS_ENABLED:
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

            email_input = SingleEmailInput(destination=instance.email, subject="Welcome to MyFinances", content=email_message)

            email = send_email(email_input)

        #     User.send_welcome_email(instance)
