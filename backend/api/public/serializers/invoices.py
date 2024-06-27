from rest_framework import serializers

from backend.models import InvoiceItem, Invoice, InvoiceProduct


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceItemField(serializers.ListField):
    child = InvoiceItemSerializer()

    def to_internal_value(self, data):
        if isinstance(data, list):
            items = []
            for item_data in data:
                serializer = InvoiceItemSerializer(data=item_data)
                if serializer.is_valid(raise_exception=True):
                    items.append(serializer.validated_data)
                else:
                    raise serializers.ValidationError("Invalid data for InvoiceItem.")
            return items
        else:
            raise serializers.ValidationError("Expected a list of items.")


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemField(required=False)
    client_id = serializers.IntegerField(required=False)

    class Meta:
        model = Invoice
        fields = "__all__"

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])

        invoice = Invoice.objects.create(**validated_data)

        if not isinstance(items_data, InvoiceProduct):
            for item_data in items_data:
                item = InvoiceItem.objects.create(invoice=invoice, **item_data)
                invoice.items.add(item)

        else:
            items_data = InvoiceItem.objects.create(
                name=items_data.name,
                description=items_data.description,
                hours=items_data.quantity,
                price_per_hour=items_data.rate,
                price=items_data.rate * items_data.quantity,
            )
            invoice.items.add(items_data)

        return invoice
