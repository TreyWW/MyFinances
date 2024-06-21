from django.db import models
from django.contrib.auth.hashers import check_password, make_password
import binascii
import os
from django.utils import timezone


class APIAuthToken(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField("Key Name", max_length=64)
    description = models.TextField("Description", blank=True, null=True)
    user = models.ForeignKey("backend.User", on_delete=models.CASCADE)
    key = models.CharField("Key", max_length=40, unique=True)
    created = models.DateTimeField("Created", auto_now_add=True)
    last_used = models.DateTimeField("Last Used", null=True, blank=True)
    expires = models.DateTimeField("Expires", null=True, blank=True, help_text="Leave blank for no expiry")
    expired = models.BooleanField("Expired", default=False, help_text="If the key has expired")
    active = models.BooleanField("Active", default=True, help_text="If the key is active")
    scopes = models.JSONField("Scopes", default=list, help_text="List of permitted scopes")
    team = models.ForeignKey("backend.Team", on_delete=models.CASCADE, null=True, blank=True, related_name="tokens")

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return self.key

    def has_expired(self):
        if not self.expires:
            return False
        return self.expires < timezone.now()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def regenerate_key(self):
        key = self.generate_key()
        self.hash_and_save(key=key)
        return key

    @classmethod
    def generate_key(cls):
        """Returns a new raw key"""
        return binascii.hexlify(os.urandom(20)).decode()

    def verify(self, key):
        return check_password(key, self.key)

    def hash_and_save(self, key=None):
        if not key:
            key = self.key
        self.key = make_password(key)
        self.save()
        return self

    def deactivate(self):
        self.active = False
        self.save()
        return self

    def has_scope(self, scope):
        return scope in self.scopes
