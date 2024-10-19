from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.hashers import check_password, make_password
import binascii
import os
from django.utils import timezone

from backend.core.models import OwnerBase, ExpiresBase


class APIAuthToken(OwnerBase, ExpiresBase):
    id = models.AutoField(primary_key=True)

    hashed_key = models.CharField("Key", max_length=128, unique=True)

    name = models.CharField("Key Name", max_length=64)
    description = models.TextField("Description", blank=True, null=True)
    created = models.DateTimeField("Created", auto_now_add=True)
    last_used = models.DateTimeField("Last Used", null=True, blank=True)
    # expires = models.DateTimeField("Expires", null=True, blank=True, help_text="Leave blank for no expiry")
    # expired = models.BooleanField("Expired", default=False, help_text="If the key has expired")
    # active = models.BooleanField("Active", default=True, help_text="If the key is active")
    scopes = models.JSONField("Scopes", default=list, help_text="List of permitted scopes")

    class AdministratorServiceTypes(models.TextChoices):
        AWS_WEBHOOK_CALLBACK = "aws_webhook_callback", "AWS Webhook Callback"
        AWS_API_DESTINATION = "aws_api_destination", "AWS API Destination"

    administrator_service_type = models.CharField("Administrator Service Type", max_length=64, blank=True, null=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return self.name

    def update_last_used(self):
        self.last_used = timezone.now()
        self.save()
        return True

    # def save(self, *args, **kwargs):
    #     return super().save(*args, **kwargs)

    def generate_key(self) -> str:
        """
        :returns: raw_key
        """

        raw = binascii.hexlify(os.urandom(20)).decode()
        self.hashed_key = self.hash_raw_key(raw)

        return raw

    @classmethod
    def hash_raw_key(cls, raw_key: str):
        return make_password(raw_key, salt="api_tokens", hasher="default")

    def verify(self, key) -> bool:
        return check_password(key, self.hashed_key)

    def deactivate(self):
        self.active = False
        self.save()
        return self

    def has_scope(self, scope):
        return scope in self.scopes
