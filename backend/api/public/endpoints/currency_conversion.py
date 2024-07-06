from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.permissions import IsAuthenticated

from backend.api.currency_converter.convert import convert_currency

from django.db import connection, OperationalError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from backend.api.public.helpers.deprecate import deprecated
from backend.api.public.permissions import IsSuperuser

from rest_framework import serializers


class CurrencyConversionSerializer(serializers.Serializer):
    init_currency = serializers.CharField(max_length=3, help_text="Initial currency code")
    target_currency = serializers.CharField(max_length=3, help_text="Target currency code")
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, help_text="Initial amount <decimal>")
    date = serializers.DateTimeField(required=False, help_text="Date of exchange <date-time>")


@permission_classes([IsAuthenticated])
@swagger_auto_schema(
    method="get",
    operation_description="Converts one currency to another.",
    responses={
        200: openapi.Response(
            description="Currency conversion result",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"converted_amount": openapi.Schema(type=openapi.TYPE_NUMBER, description="The converted amount")},
                required=["converted_amount", "init_currency", "target_currency", "amount"],
            ),
            examples={
                "application/json": {
                    "converted_amount": 50.0,
                    "init_currency": "USD",
                    "target_currency": "EUR",
                    "amount": 100.0,
                }
            },
        ),
        400: openapi.Response(
            description="Error response",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={"error": openapi.Schema(type=openapi.TYPE_STRING, description="An error message")},
                required=["error"],
            ),
            examples={"application/json": {"error": "Invalid currency code"}},
        ),
    },
    query_serializer=CurrencyConversionSerializer,
    deprecated=True,
)
@api_view(["GET"])
@deprecated
def convert_currency_endpoint(request):
    if request.method == "GET":
        serializer = CurrencyConversionSerializer(data=request.query_params)
        if serializer.is_valid():
            init_currency = serializer.validated_data["init_currency"]
            target_currency = serializer.validated_data["target_currency"]
            amount = serializer.validated_data["amount"]
            date = serializer.validated_data.get("date")

            try:
                converted_amount = convert_currency(init_currency, target_currency, amount, date)
                return Response({"converted_amount": converted_amount})
            except ValueError as e:
                return Response({"error": str(e)}, status=400)

        return Response(serializer.errors, status=400)
