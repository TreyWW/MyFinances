from rest_framework import serializers

from backend.models import InvoiceURL


class InvoiceURLCreatedSerializer(serializers.Serializer):

    id = serializers.IntegerField(label="Invoice ID")
    success = serializers.BooleanField(label="Was code generated successfully")
    uuid = serializers.CharField(label="Invoice access code")
    # url = serializers.URLField(label="Invoice access full URL")