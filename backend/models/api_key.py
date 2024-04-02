from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from backend.models.utils import RandomAPICode


class APIKey(models.Model):
    class ServiceTypes(models.TextChoices):
        AWS_API_DESTINATION = "aws_api_destination"

    service = models.CharField(max_length=20, choices=ServiceTypes.choices, null=True)
    key = models.CharField(max_length=100, default=RandomAPICode)
    last_used = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "API Key"
        verbose_name_plural = "API Keys"

    def __str__(self):
        return self.service

    def verify(self, key):
        return check_password(key, self.key)

    def hash(self):
        self.key = make_password(f"{self.id}:{self.key}")
        self.save()
