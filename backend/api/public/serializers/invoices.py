from rest_framework import serializers

from backend.models import InvoiceItem, Invoice, InvoiceProduct


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["name", "description", "hours", "price_per_hour"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True)
    client_id = serializers.IntegerField(required=False)

    class Meta:
        model = Invoice
        fields = "__all__"

    # def create(self, validated_data):
    #     items_data = validated_data.pop('items')
    #     invoice = Invoice.objects.create(**validated_data)
    #     for item_data in items_data:
    #         InvoiceItem.objects.create(invoice=invoice, **item_data)
    #     return invoice


class InvoiceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceProduct
        fields = ["id", "name", "description", "rate", "quantity"]
