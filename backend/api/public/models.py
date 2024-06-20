import binascii
import os

from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils.translation import gettext_lazy as _


class APIAuthToken(models.Model):
    user = models.ForeignKey("backend.User", on_delete=models.CASCADE)
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return self.key

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
