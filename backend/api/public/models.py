import binascii
import os

from django.db import models
from django.utils.translation import gettext_lazy as _


class APIAuthToken(models.Model):
    user = models.ForeignKey("backend.User", on_delete=models.CASCADE)
    key = models.CharField(_("Key"), max_length=40, primary_key=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @classmethod
    def generate_key(cls):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
