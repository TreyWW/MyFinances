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
        fields = [
            "date_due",
            "date_issued",
            "currency",
            "client_id",
            "client_name",
            "client_company",
            "client_address",
            "client_city",
            "client_county",
            "client_country",
            "client_is_representative",
            "self_name",
            "self_company",
            "self_address",
            "self_city",
            "self_county",
            "self_country",
            "notes",
            "invoice_number",
            "vat_number",
            "logo",
            "reference",
            "sort_code",
            "account_number",
            "account_holder_name",
            "items",
        ]

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
