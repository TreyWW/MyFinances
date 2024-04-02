from django.db import models
from backend.models.user import User, Team
from backend.models.utils import USER_OR_ORGANIZATION_CONSTRAINT

class Client(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    organization = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    is_representative = models.BooleanField(default=False)

    address = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        constraints = [USER_OR_ORGANIZATION_CONSTRAINT()]

    def __str__(self):
        return self.name
