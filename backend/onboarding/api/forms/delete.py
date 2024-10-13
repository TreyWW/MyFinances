from django.contrib import messages
from django.shortcuts import render

from backend.core.types.requests import WebRequest
from backend.decorators import web_require_scopes
from backend.models import OnboardingForm, AuditLog


@web_require_scopes("onboarding:write", True, True)
def delete_form_endpoint(request: WebRequest, uuid):
    form: OnboardingForm | None = OnboardingForm.filter_by_owner(request.actor).filter(uuid=uuid).first()

    if not form:
        messages.error(request, "Form not found")
        return render(request, "base/toast.html")

    AuditLog.objects.create(
        actor=request.user, owner=request.actor, action="onboarding.form.delete", description=f"Deleted form {form.title} | {form.uuid}"
    )

    form.delete()

    messages.success(request, "Form deleted")
    return render(request, "base/toast.html")
