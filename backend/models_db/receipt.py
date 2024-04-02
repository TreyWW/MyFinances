from django.db import models
from uuid import uuid4

from settings import settings
from backend.models import User, Team
from backend.models_db.utils import USER_OR_ORGANIZATION_CONSTRAINT


class Receipt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    organization = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="receipts", storage=settings.CustomPrivateMediaStorage())
    total_price = models.FloatField(null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    date_uploaded = models.DateTimeField(auto_now_add=True)
    receipt_parsed = models.JSONField(null=True, blank=True)
    merchant_store = models.CharField(max_length=255, blank=True, null=True)
    purchase_category = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        constraints = [USER_OR_ORGANIZATION_CONSTRAINT()]


class ReceiptDownloadToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid4, editable=False, unique=True)
