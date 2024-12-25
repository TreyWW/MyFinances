from rest_framework import serializers

from backend.finance.models import InvoiceItem, Invoice


class InvoiceItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)

    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        exclude = ("user", "organization", "client_to")
        # fields = "__all__"

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        invoice = Invoice.objects.create(**validated_data)

        for item_data in items_data:
            item = InvoiceItem.objects.create(invoice=invoice, **item_data)
            invoice.items.add(item)

        return invoice
