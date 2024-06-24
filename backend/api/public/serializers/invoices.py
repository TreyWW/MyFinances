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


class InvoiceItemOrProductField(serializers.Field):
    def to_representation(self, value):
        if isinstance(value, InvoiceItem):
            return InvoiceItemSerializer(value).data
        elif isinstance(value, InvoiceProduct):
            return InvoiceProductSerializer(value).data
        return super().to_representation(value)

    def to_internal_value(self, data):
        # product_id = self.context.get('product_id')
        #
        # if product_id:
        #     try:
        #         product = InvoiceProduct.objects.get(id=product_id)
        #         return product
        #     except InvoiceProduct.DoesNotExist:
        #         raise serializers.ValidationError("InvoiceProduct not found.")

        if isinstance(data, list):
            items = []
            for item_data in data:
                if "product_id" in item_data:
                    try:
                        product = InvoiceProduct.objects.get(id=item_data["product_id"])
                        items.append(product)
                    except InvoiceProduct.DoesNotExist:
                        raise serializers.ValidationError("InvoiceProduct not found.")
                else:
                    serializer = InvoiceItemSerializer(data=item_data)
                    if serializer.is_valid(raise_exception=True):
                        items.append(serializer.validated_data)
                    else:
                        raise serializers.ValidationError("Invalid data for InvoiceItem.")
            return items
        else:
            raise serializers.ValidationError("Expected a list of items.")


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemOrProductField(required=False)
    client_id = serializers.IntegerField(required=False)

    class Meta:
        model = Invoice
        fields = "__all__"

    def create(self, validated_data):
        items_data = validated_data.pop("items", [])
        invoice = Invoice.objects.create(**validated_data)

        for item_data in items_data:
            if isinstance(item_data, dict):
                InvoiceItem.objects.create(invoice=invoice, **item_data)
            else:
                invoice.items.add(item_data)
        return invoice
