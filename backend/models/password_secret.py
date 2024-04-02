from django.db import models
from backend.models.user import User


class PasswordSecret(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="password_secrets")
    secret = models.TextField(max_length=300)
    expires = models.DateTimeField(null=True, blank=True)
