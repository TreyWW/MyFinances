from rest_framework import serializers

from backend.models import Receipt, ReceiptDownloadToken


class ReceiptReturnedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Receipt
        fields = [
            "id",
            "user",
            "name",
            # "image",
            "total_price",
            "date",
            "date_uploaded",
            # "receipt_parsed",
            # "merchant_store",
            "purchase_category",
        ]

    id = serializers.IntegerField(label="Receipt ID")
    user = serializers.IntegerField(
        source="user.id",
        required=True,
        label="User ID",
        help_text="The receipt owners User ID",
    )

    name = serializers.CharField(
        label="Receipt Name",
        help_text="The custom name of the receipt",
        required=True,
    )

    total_price = serializers.FloatField(
        label="Total Price", help_text="The total price of the receipt"
    )

    date = serializers.DateTimeField(
        label="Receipt Date", help_text="The date of the receipt", required=False
    )

    date_uploaded = serializers.DateTimeField(
        label="Date Uploaded",
        help_text="The date the receipt was uploaded",
        required=True,
    )

    purchase_category = serializers.CharField(
        label="Purchase Category",
        help_text="The category of the purchase",
        required=False,
    )



class ReceiptDownloadTokenReturnedSerializer(serializers.Serializer):
    class Meta:
        model = ReceiptDownloadToken
        fields = [
            "success",
            "token",
            "url"
        ]

    success = serializers.BooleanField(label="Was token generated successfully")
    token = serializers.CharField(label="Receipt download token")
    url = serializers.URLField(label="Receipt download full URL")