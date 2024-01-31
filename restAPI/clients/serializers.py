from rest_framework import serializers

from backend.models import Client


class ClientReturnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "active",
            "name",
            "company",
            "is_representative",
        ]
