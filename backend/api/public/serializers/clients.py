from rest_framework import serializers

from backend.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        exclude = ("organization", "user", "email_verified")
