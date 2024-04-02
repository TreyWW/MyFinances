from django.db import models

from backend.models import Team, User

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    organization = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} - {self.date}"


class LoginLog(models.Model):
    class ServiceTypes(models.TextChoices):
        MANUAL = "manual"
        MAGIC_LINK = "magic_link"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=14, choices=ServiceTypes.choices, default="manual")
    date = models.DateTimeField(auto_now_add=True)
