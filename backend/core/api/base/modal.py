from __future__ import annotations

from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from backend.core.api.public import APIAuthToken
from backend.core.api.public.permissions import SCOPE_DESCRIPTIONS

from backend.clients.models import Client
from backend.finance.models import InvoiceURL, Invoice, Receipt
from backend.models import QuotaLimit, Organization, UserSettings
from backend.core.types.requests import WebRequest
from backend.core.utils.feature_flags import get_feature_status
from backend.core.service.defaults.get import get_account_defaults


def open_modal(request: WebRequest, modal_name, context_type=None, context_value=None):
    try:
        context = {}
        template_name = f"modals/{modal_name}.html"
        if context_type and context_value:
            if context_type == "profile_picture":
                try:
                    context["users_profile_picture"] = request.user.user_profile.profile_picture_url
                except UserSettings.DoesNotExist:
                    pass
            elif context_type == "accept_invite_with_code":
                context["code"] = context_value
            elif context_type == "leave_team":
                if request.user.teams_joined.filter(id=context_value).exists():
                    context["team"] = Organization.objects.filter(id=context_value).first()
            elif context_type == "edit_receipt":
                try:
                    receipt = Receipt.objects.get(pk=context_value)
                except Receipt.DoesNotExist:
                    return render(request, template_name, context)
                receipt_date = receipt.date.strftime("%Y-%m-%d") if receipt.date else ""
                context = {
                    "modal_id": f"modal_{receipt.id}_receipts_upload",
                    "receipt_id": context_value,
                    "receipt_name": receipt.name,
                    "receipt_date": receipt_date,
                    "merchant_store_name": receipt.merchant_store,
                    "purchase_category": receipt.purchase_category,
                    "total_price": receipt.total_price,
                    "has_receipt_image": True if receipt.image else False,
                    "edit_flag": True,
                }
            elif context_type == "upload_receipt":
                context["modal_id"] = f"modal_receipts_upload"
            elif context_type == "edit_invoice_to":
                invoice = context_value
                try:
                    invoice = Invoice.filter_by_owner(request.actor).get(id=invoice)
                except Invoice.DoesNotExist:
                    return render(request, template_name, context)

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
            elif context_type == "edit_invoice_from":
                invoice = context_value
                try:
                    invoice = Invoice.filter_by_owner(request.actor).get(id=invoice)
                except Invoice.DoesNotExist:
                    return render(request, template_name, context)

                context["from_name"] = invoice.self_name
                context["from_company"] = invoice.self_company
                context["from_address"] = invoice.self_address
                context["from_city"] = invoice.self_city
                context["from_county"] = invoice.self_county
                context["from_country"] = invoice.self_country
            elif context_type == "create_invoice_from":
                defaults = get_account_defaults(request.actor)

                context["from_name"] = getattr(defaults, f"invoice_from_name")
                context["from_company"] = getattr(defaults, f"invoice_from_company")
                context["from_address"] = getattr(defaults, f"invoice_from_address")
                context["from_city"] = getattr(defaults, f"invoice_from_city")
                context["from_county"] = getattr(defaults, f"invoice_from_county")
                context["from_country"] = getattr(defaults, f"invoice_from_country")
            elif context_type == "invoice":
                try:
                    invoice = Invoice.objects.get(id=context_value)
                    if invoice.has_access(request.user):
                        context["invoice"] = invoice
                except Invoice.DoesNotExist:
                    ...
            elif context_type == "quota":
                try:
                    quota = QuotaLimit.objects.prefetch_related("quota_overrides").get(slug=context_value)
                    context["quota"] = quota
                    context["current_limit"] = quota.get_quota_limit(user=request.user, quota_limit=quota)
                    usage = quota.strict_get_quotas(user=request.user, quota_limit=quota)
                    context["quota_usage"] = usage.count() if usage != "Not Available" else "Not available"
                    print(context["quota_usage"])
                except QuotaLimit.DoesNotExist:
                    ...
            elif context_type == "invoice_reminder":
                try:
                    invoice = (
                        Invoice.objects.only("id", "client_email", "client_to__email").select_related("client_to").get(id=context_value)
                    )
                except Invoice.DoesNotExist:
                    return render(request, template_name, context)

                if invoice.has_access(request.user):
                    context["invoice"] = invoice
                else:
                    messages.error(request, "You don't have access to this invoice")
                    return render(request, "base/toasts.html")

                # above_quota_usage = False  # quota_usage_check_under(request, "invoices-schedules", api=True, htmx=True)

                # if not isinstance(above_quota_usage, bool):  #     context["above_quota_usage"] = True

            else:
                context[context_type] = context_value

        if modal_name == "send_single_email" or modal_name == "send_bulk_email":
            if not get_feature_status("areUserEmailsAllowed"):
                messages.error(request, "Emails are disabled")
                return render(request, "base/toast.html")
            context["content_min_length"] = 64
            quota = QuotaLimit.objects.prefetch_related("quota_overrides").get(slug="emails-email_character_count")
            context["content_max_length"] = quota.get_quota_limit(user=request.user, quota_limit=quota)
            context["email_list"] = Client.filter_by_owner(owner=request.actor).filter(email__isnull=False).values_list("email", flat=True)

            if context_type == "invoice_code_send":
                invoice_url: InvoiceURL | None = InvoiceURL.objects.filter(uuid=context_value).prefetch_related("invoice").first()

                if not invoice_url or not invoice_url.invoice.has_access(request.user):
                    messages.error(request, "You don't have access to this invoice")
                    return render(request, "base/toast.html", {"autohide": False})

                context["invoice"] = invoice_url.invoice
                context["selected_clients"] = [
                    invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email
                    for value in [
                        invoice_url.invoice.client_to.email if invoice_url.invoice.client_to else invoice_url.invoice.client_email
                    ]
                    if value is not None
                ]

                context["email_list"] = list(context["email_list"]) + context["selected_clients"]

        elif modal_name == "invoices_to_destination":
            if existing_client := request.GET.get("client"):
                context["existing_client_id"] = existing_client
        elif modal_name in ["generate_api_key", "edit_team_member_permissions", "team_create_user"]:
            # example
            # "clients": {
            #     "description": "Access customer details",
            #     "options": ["read", "write"]
            # },
            context["permissions"] = [
                {"name": group, "description": perms["description"], "options": perms["options"]}
                for group, perms in SCOPE_DESCRIPTIONS.items()
            ]
            context["APIAuthToken_types"] = APIAuthToken.AdministratorServiceTypes

        if modal_name == "edit_team_member_permissions":
            team = request.user.logged_in_as_team
            if team:
                for_user = team.members.filter(id=context_value).first()
                for_user_perms = team.permissions.filter(user=for_user).first()
                if for_user:
                    context["editing_user"] = for_user
                    context["user_current_scopes"] = for_user_perms.scopes if for_user_perms else []

        return render(request, template_name, context)
    except ValueError as e:
        print(f"Something went wrong with loading modal {modal_name}. Error: {e}")
        return HttpResponseBadRequest("Something went wrong")
