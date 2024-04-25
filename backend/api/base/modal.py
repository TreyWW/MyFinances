from __future__ import annotations

from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.shortcuts import render

from backend.models import Client, Receipt
from backend.models import Invoice
from backend.models import QuotaLimit
from backend.models import Team
from backend.models import UserSettings
from backend.types.htmx import HtmxHttpRequest
from backend.utils.feature_flags import get_feature_status
from backend.utils.quota_limit_ops import quota_usage_check_under


# Still working on


def open_modal(request: HtmxHttpRequest, modal_name, context_type=None, context_value=None):
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
                    context["team"] = Team.objects.filter(id=context_value).first()
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
                    invoice = Invoice.objects.get(user=request.user, id=invoice)
                except Invoice.DoesNotExist:
                    return render(request, template_name, context)

                if invoice.client_to:
                    context["to_name"] = invoice.client_to.name
                    context["to_company"] = invoice.client_to.company
                    context["to_address"] = invoice.client_to.address
                    context["existing_client_id"] = invoice.client_to.id
                    # context["to_city"] = invoice.client_to.city
                    # context["to_county"] = invoice.client_to.county
                    # context["to_country"] = invoice.client_to.country
                else:
                    context["to_name"] = invoice.client_name
                    context["to_company"] = invoice.client_company
                    context["to_address"] = invoice.client_address
                    # context["to_city"] = invoice.client_city
                    # context["to_county"] = invoice.client_county
                    # context["to_country"] = invoice.client_country
            elif context_type == "edit_invoice_from":
                invoice = context_value
                try:
                    invoice = Invoice.objects.get(user=request.user, id=invoice)
                except Invoice.DoesNotExist:
                    return render(request, template_name, context)

                context["from_name"] = invoice.self_name
                context["from_company"] = invoice.self_company
                context["from_address"] = invoice.self_address
                context["from_city"] = invoice.self_city
                context["from_county"] = invoice.self_county
                context["from_country"] = invoice.self_country
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

                above_quota_usage = quota_usage_check_under(request, "invoices-schedules", api=True, htmx=True)

                if not isinstance(above_quota_usage, bool):
                    context["above_quota_usage"] = True

            else:
                context[context_type] = context_value

        if modal_name == "send_single_email" or modal_name == "send_bulk_email":
            if not get_feature_status("areUserEmailsAllowed"):
                messages.error(request, "Emails are disabled")
                return render(request, "base/toast.html")
            context["content_min_length"] = 64
            quota = QuotaLimit.objects.prefetch_related("quota_overrides").get(slug="emails-email_character_count")
            context["content_max_length"] = quota.get_quota_limit(user=request.user, quota_limit=quota)
            if request.user.logged_in_as_team:
                clients = Client.objects.filter(organization=request.user.logged_in_as_team)
            else:
                clients = Client.objects.filter(user=request.user)
            context["email_list"] = clients

        return render(request, template_name, context)
    except ValueError as e:
        print(f"Something went wrong with loading modal {modal_name}. Error: {e}")
        return HttpResponseBadRequest("Something went wrong")
