from django.contrib import messages
from django.shortcuts import render
from django.views.decorators.http import require_POST

from backend.core.service.defaults.get import get_account_defaults
from backend.decorators import web_require_scopes
from backend.core.types.requests import WebRequest


@require_POST
@web_require_scopes(["email_templates:write", "account_defaults:write"], True, True)
def save_email_template(request: WebRequest, template: str):
    template = template.lower().strip()
    content = request.POST.get("content")

    if template not in ["invoice_created", "invoice_overdue", "invoice_cancelled"]:
        messages.error(request, f"Invalid template: {template}")
        return render(request, "base/toast.html")

    if content is None:
        messages.error(request, f"Missing content for template: {template}")
        return render(request, "base/toast.html")

    acc_defaults = get_account_defaults(request.actor)

    setattr(acc_defaults, f"email_template_recurring_invoices_{template}", content)

    acc_defaults.save()

    messages.success(request, f"Email template '{template}' saved successfully")

    return render(request, "base/toast.html")
