from core.service.modals.registry import Modal
from core.types.requests import WebRequest
from core.utils.feature_flags import get_feature_status
from django.contrib import messages
from django.shortcuts import render

from backend.finance.models import InvoiceURL
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
            return render(request, "base/toast.html")

        context = self.get_context(request)

        if request.GET.get("type") == "invoice_code_send":
            invoice_url: InvoiceURL | None = InvoiceURL.objects.filter(uuid=request.GET.get("code")).prefetch_related("invoice").first()

            if not invoice_url or not invoice_url.invoice.has_access(request.user):
                messages.error(request, "You don't have access to this invoice")
                return render(request, "base/toast.html", {"autohide": False})

            context["invoice"] = invoice_url.invoice
            context["selected_clients"] = [
                invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email
                for value in [invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email]
                if value is not None
            ]

            context["email_list"] = list(context["email_list"]) + context["selected_clients"]

        return render(request, self.get_template_name(), context)
