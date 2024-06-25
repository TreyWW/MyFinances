from rest_framework import serializers

from backend.models import InvoiceItem, Invoice, InvoiceProduct


class InvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = "__all__"


class InvoiceProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceProduct
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
        from backend.service.invoices.create.create import serializer_create

        return serializer_create(validated_data)
