from core.service.modals.registry import Modal
from core.types.requests import WebRequest
from core.utils.feature_flags import get_feature_status
from django.contrib import messages
from django.shortcuts import render

from backend.finance.models import InvoiceURL, Invoice, Receipt
from backend.finance.service.defaults.get import get_account_defaults
from backend.models import Client


class InvoicesToDestinationModal(Modal):
    modal_name = "invoices_to_destination"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        if existing_client := request.GET.get("client"):
            context["existing_client_id"] = existing_client

        return render(request, self.get_template_name(), context)


class EmailContext:
    def get_context(self, request: WebRequest) -> dict:
        return {
            "content_min_length": 64,
            "content_max_length": 1000,
            "email_list": Client.filter_by_owner(owner=request.actor).filter(email__isnull=False).values_list("email", flat=True),
        }


class SendSingleEmailModal(Modal, EmailContext):
    modal_name = "send_single_email"

    def get(self, request: WebRequest):
        if not get_feature_status("areUserEmailsAllowed"):
            messages.error(request, "Emails are disabled")
            return render(request, "core/base/toast.html")

        context = self.get_context(request)

        if request.GET.get("type") == "invoice_code_send":
            invoice_url: InvoiceURL | None = InvoiceURL.objects.filter(uuid=request.GET.get("code")).prefetch_related("invoice").first()

            if not invoice_url or not invoice_url.invoice.has_access(request.user):
                messages.error(request, "You don't have access to this invoice")
                return render(request, "core/base/toast.html", {"autohide": False})

            context["invoice"] = invoice_url.invoice
            context["selected_clients"] = [
                invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email
                for value in [invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email]
                if value is not None
            ]

            context["email_list"] = list(context["email_list"]) + context["selected_clients"]

        return render(request, self.get_template_name(), context)


class EditReceiptModal(Modal):
    modal_name = "edit_receipt"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        try:
            receipt = Receipt.filter_by_owner(request.actor).get(pk=request.GET.get("receipt_id"))
        except Receipt.DoesNotExist:
            return self.Response(request, context)

        receipt_date = receipt.date.strftime("%Y-%m-%d") if receipt.date else ""
        context.update(
            {
                "modal_id": f"modal_{receipt.id}_receipts_upload",
                "receipt_id": request.GET.get("receipt_id"),
                "receipt_name": receipt.name,
                "receipt_date": receipt_date,
                "merchant_store_name": receipt.merchant_store,
                "purchase_category": receipt.purchase_category,
                "total_price": receipt.total_price,
                "has_receipt_image": True if receipt.image else False,
                "edit_flag": True,
            }
        )

        return self.Response(request, context)


class UploadReceiptModal(Modal):
    modal_name = "upload_receipt"
    template_name = "modals/receipts_upload.html"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        context.update({"modal_id": "modal_receipts_upload"})

        return self.Response(request, context)


class EditInvoiceToModal(Modal):
    modal_name = "edit_invoice_to"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        invoice_id = request.GET.get("invoice_id")

        try:
            invoice = Invoice.filter_by_owner(request.actor).get(id=invoice_id)  # todo: add permission checks
        except Invoice.DoesNotExist:
            return self.Response(request, context)

        if invoice.client_to:
            context["to_name"] = invoice.client_to.name
            context["to_company"] = invoice.client_to.company
            context["to_email"] = invoice.client_to.email
            context["to_address"] = invoice.client_to.address
            context["existing_client_id"] = (
                invoice.client_to.id
            )  # context["to_city"] = invoice.client_to.city  # context["to_county"] = invoice.client_to.county  # context["to_country"] = invoice.client_to.country
        else:
            context["to_name"] = invoice.client_name
            context["to_company"] = invoice.client_company
            context["to_email"] = invoice.client_email
            context["is_representative"] = invoice.client_is_representative
            context["to_address"] = (
                invoice.client_address
            )  # context["to_city"] = invoice.client_city  # context["to_county"] = invoice.client_county  # context["to_country"] = invoice.client_country

        return self.Response(request, context)


class EditInvoiceFromModal(Modal):
    modal_name = "edit_invoice_from"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        invoice_id = request.GET.get("invoice_id")

        try:
            invoice = Invoice.filter_by_owner(request.actor).get(id=invoice_id)  # todo: add permission checks
        except Invoice.DoesNotExist:
            return self.Response(request, context)

        context["from_name"] = invoice.self_name
        context["from_company"] = invoice.self_company
        context["from_address"] = invoice.self_address
        context["from_city"] = invoice.self_city
        context["from_county"] = invoice.self_county
        context["from_country"] = invoice.self_country
        return self.Response(request, context)


# create_invoice_from
class CreateInvoiceFromModal(Modal):
    modal_name = "create_invoice_from"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        defaults = get_account_defaults(request.actor)

        context["from_name"] = getattr(defaults, f"invoice_from_name")
        context["from_company"] = getattr(defaults, f"invoice_from_company")
        context["from_address"] = getattr(defaults, f"invoice_from_address")
        context["from_city"] = getattr(defaults, f"invoice_from_city")
        context["from_county"] = getattr(defaults, f"invoice_from_county")
        context["from_country"] = getattr(defaults, f"invoice_from_country")

        return self.Response(request, context)


class InvoiceContext:
    def get_context(self, request: WebRequest) -> dict:
        try:
            invoice = Invoice.filter_by_owner(request.actor).get(id=request.GET.get("invoice_id"))
            if invoice.has_access(request.user):
                return {"invoice": invoice}
        except Invoice.DoesNotExist:
            return {}


class EditInvoiceDiscountModal(Modal, InvoiceContext):
    modal_name = "invoices_edit_discount"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        return self.Response(request, context)


# class ViewQuotaLimitInfoModal(Modal):
#     modal_name = 'view_quota_limit_info'
#
#     def get(self, request: WebRequest):
#         context = self.get_context(request)
#
#         try:
#             quota = QuotaLimit.objects.prefetch_related("quota_overrides").get(slug=context_value)
#             context["quota"] = quota
#             context["current_limit"] = quota.get_quota_limit(user=request.user, quota_limit=quota)
#             usage = quota.strict_get_quotas(user=request.user, quota_limit=quota)
#             context["quota_usage"] = usage.count() if usage != "Not Available" else "Not available"
#             print(context["quota_usage"])
#         except QuotaLimit.DoesNotExist:
#             ...
#
#         return self.Response(request, context)


class CreateInvoiceReminderModal(Modal):
    modal_name = "create_invoice_reminder"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        try:
            invoice = Invoice.filter_by_owner(request.actor).get(id=request.GET.get("invoice_id"))
            if invoice.has_access(request.user):
                context["invoice"] = invoice
            else:
                messages.error(request, "You don't have access to this invoice")
                return render(request, "core/base/toasts.html")
        except Invoice.DoesNotExist:
            return self.Response(request, context)

        return self.Response(request, context)


class SendEmailContext:
    def get_context(self, request: WebRequest) -> dict:
        if not get_feature_status("areUserEmailsAllowed"):
            messages.error(request, "Emails are disabled")
            return render(request, "core/base/toast.html")

        context = {}

        context["content_min_length"] = 64
        # quota = QuotaLimit.objects.prefetch_related("quota_overrides").get(slug="emails-email_character_count")
        # context["content_max_length"] = quota.get_quota_limit(user=request.user, quota_limit=quota)
        context["content_max_length"] = 1000

        context["email_list"] = Client.filter_by_owner(owner=request.actor).filter(email__isnull=False).values_list("email", flat=True)

        return context


class InvoiceCodeSendModal(Modal, SendEmailContext):
    modal_name = "invoice_code_send"

    def get(self, request: WebRequest):
        context = self.get_context(request)

        invoice_url: InvoiceURL | None = InvoiceURL.objects.filter(uuid=request.GET.get("code")).prefetch_related("invoice").first()

        if not invoice_url or not invoice_url.invoice.has_access(request.user):
            messages.error(request, "You don't have access to this invoice")
            return render(request, "core/base/toast.html", {"autohide": False})

        context["invoice"] = invoice_url.invoice
        context["selected_clients"] = [
            invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email
            for value in [invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email]
            if value is not None
        ]

        context["email_list"] = list(context["email_list"]) + context["selected_clients"]

        return self.Response(request, context)


class GenerateReportModal(Modal):
    modal_name = "generate_report"
