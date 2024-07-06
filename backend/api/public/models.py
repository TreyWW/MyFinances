from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.hashers import check_password, make_password
import binascii
import os
from django.utils import timezone

from backend.models import OwnerBase


class APIAuthToken(OwnerBase):
    id = models.AutoField(primary_key=True)

    hashed_key = models.CharField("Key", max_length=128, unique=True)

    name = models.CharField("Key Name", max_length=64)
    description = models.TextField("Description", blank=True, null=True)
    created = models.DateTimeField("Created", auto_now_add=True)
    last_used = models.DateTimeField("Last Used", null=True, blank=True)
    expires = models.DateTimeField("Expires", null=True, blank=True, help_text="Leave blank for no expiry")
    expired = models.BooleanField("Expired", default=False, help_text="If the key has expired")
    active = models.BooleanField("Active", default=True, help_text="If the key is active")
    scopes = models.JSONField("Scopes", default=list, help_text="List of permitted scopes")

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return self.name

    def has_expired(self):
        if not self.expires:
            return False
        return self.expires < timezone.now()

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
