from datetime import datetime, date

from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from rest_framework import status
from rest_framework.response import Response

from backend.api.public.serializers.invoices import InvoiceSerializer
from backend.models import Invoice, InvoiceItem, Client, QuotaUsage, InvoiceProduct
from backend.service.clients.validate import validate_client
from backend.types.htmx import HtmxHttpRequest


def get_invoice_context(request: HtmxHttpRequest) -> dict:
    context: dict = {
        "clients": Client.objects.filter(user=request.user),
        "existing_products": InvoiceProduct.objects.filter(user=request.user),
    }

    if client_id := request.GET.get("client"):
        try:
            client: Client = validate_client(request, client_id)
            context["existing_client"] = client
        except (Client.DoesNotExist, PermissionDenied, ValidationError):
            ...

    if issue_date := request.GET.get("issue_date"):
        try:
            date.fromisoformat(issue_date)
            context["issue_date"] = issue_date
        except ValueError:
            ...

    if due_date := request.GET.get("due_date"):
        try:
            date.fromisoformat(due_date)
            context["due_date"] = due_date
        except ValueError:
            ...

    if sort_code := (request.GET.get("sort_code") or "").replace("-", ""):
        if len(sort_code) == 6:
            if len(sort_code) >= 2:
                sort_code = sort_code[0:2] + "-" + sort_code[2:]
            if len(sort_code) >= 5:
                sort_code = sort_code[0:5] + "-" + sort_code[5:]
            context["sort_code"] = sort_code

    return context


def create_invoice_items(request: HtmxHttpRequest):
    return [
        InvoiceItem.objects.create(name=row[0], description=row[1], hours=row[2], price_per_hour=row[3])
        for row in zip(
            request.POST.getlist("service_name[]"),
            request.POST.getlist("service_description[]"),
            request.POST.getlist("hours[]"),
            request.POST.getlist("price_per_hour[]"),
        )
    ]


def save_invoice(request: HtmxHttpRequest, invoice_items):
    currency = request.user.user_profile.currency

    invoice = Invoice(
        date_due=datetime.strptime(request.POST.get("date_due"), "%Y-%m-%d").date(),
        date_issued=request.POST.get("date_issued"),
        currency=currency,
    )

    if request.user.logged_in_as_team:
        invoice.organization = request.user.logged_in_as_team
    else:
        invoice.user = request.user

    if request.POST.get("selected_client"):
        try:
            client = Client.objects.get(user=request.user, id=request.POST.get("selected_client", ""))
            invoice.client_to = client
        except Client.DoesNotExist:
            messages.error(request, "Client not found")
            invoice.delete()
            return None
    else:
        invoice.client_name = request.POST.get("to_name")
        invoice.client_company = request.POST.get("to_company")
        invoice.client_address = request.POST.get("to_address")
        invoice.client_city = request.POST.get("to_city")
        invoice.client_county = request.POST.get("to_county")
        invoice.client_country = request.POST.get("to_country")
        invoice.client_is_representative = True if request.POST.get("is_representative") == "on" else False

    invoice.self_name = request.POST.get("from_name")
    invoice.self_company = request.POST.get("from_company")
    invoice.self_address = request.POST.get("from_address")
    invoice.self_city = request.POST.get("from_city")
    invoice.self_county = request.POST.get("from_county")
    invoice.self_country = request.POST.get("from_country")

    invoice.notes = request.POST.get("notes")
    invoice.invoice_number = request.POST.get("invoice_number")
    invoice.vat_number = request.POST.get("vat_number")
    invoice.logo = request.FILES.get("logo")
    invoice.reference = request.POST.get("reference")
    invoice.sort_code = request.POST.get("sort_code")
    invoice.account_number = request.POST.get("account_number")
    invoice.account_holder_name = request.POST.get("account_holder_name")

    invoice.payment_status = invoice.dynamic_payment_status

    invoice.save()
    invoice.items.set(invoice_items)

    QuotaUsage.create_str(request.user, "invoices-count", invoice.id)

    return invoice


def invoice_save(request):
    for key, value in request.query_params.items():
        request.data[key] = value

    serializer = InvoiceSerializer(data=request.data)
    if serializer.is_valid():
        if request.team:
            team = request.team
            if "client_to" in request.data and request.data["client_to"]:
                try:
                    client = Client.objects.get(organization=team, id=request.data["client_to"])
                    serializer.validated_data["client_to"] = client
                except Client.DoesNotExist:
                    return Response({"error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

            if "product_id" in request.data and request.data["product_id"]:
                try:
                    product = InvoiceProduct.objects.get(organization=team, id=request.data["product_id"])
                    serializer.validated_data["items"] = product
                except InvoiceProduct.DoesNotExist:
                    return Response({"error": "InvoiceProduct not found"}, status=status.HTTP_400_BAD_REQUEST)

            invoice = serializer.save(organization=team)
        else:
            user = request.user
            if "client_to" in request.data and request.data["client_to"]:
                try:
                    client = Client.objects.get(user=user, id=request.data["client_to"])
                    serializer.validated_data["client_to"] = client
                except Client.DoesNotExist:
                    return Response({"error": "Client not found"}, status=status.HTTP_400_BAD_REQUEST)

            if "product_id" in request.data and request.data["product_id"]:
                try:
                    product = InvoiceProduct.objects.get(user=user, id=request.data["product_id"])
                    serializer.validated_data["items"] = product
                except InvoiceProduct.DoesNotExist:
                    return Response({"error": "InvoiceProduct not found"}, status=status.HTTP_400_BAD_REQUEST)

            invoice = serializer.save(user=user)
        return Response({"invoice_id": invoice.id}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def serializer_create(validated_data):
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
