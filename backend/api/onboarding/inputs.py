from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

from backend.service.onboarding.settings import get_valid_form, get_valid_form_field
from backend.types.requests import WebRequest
from backend.views.core.onboarding import OnboardingForm, OnboardingField


def new_input_endpoint(request: WebRequest, form_uuid: str) -> HttpResponse:
    new_form_name = request.POST.get("form_name")
    context: dict = {}

    try:
        form = get_valid_form(form_uuid, request.actor)
    except OnboardingForm.DoesNotExist:
        messages.error(request, "Form not found")
        if request.htmx:
            response = render(request, "base/toast.html")
        else:
            response = HttpResponse(status=404)
        return response

    field = form.fields.create(type=OnboardingField.FieldTypes.TEXT, label="Untitled question", name="todo")

    context["field"] = field

    return render(request, "pages/onboarding/form_builder/edit/input_container.html", context)


def save_field_endpoint(request: WebRequest, form_uuid: str, field_uuid: str) -> HttpResponse:
    field_label = request.POST.get("field_label")
    field_type = request.POST.get("field_type")
    field_required = request.POST.get("field_required")
    required_input_change = request.POST.get("required_input_change")

    context: dict = {}

    try:
        field = get_valid_form_field(form_uuid, field_uuid, request.actor)
    except OnboardingForm.DoesNotExist:
        return handle_error(request, "Form not found", 404)
    except OnboardingField.DoesNotExist:
        return handle_error(request, "Field not found", 404)

    if field_label:
        field.label = field_label

    if required_input_change:
        field.required = True if field_required == "on" else False

    if field_type:
        field.type = field_type

    try:
        field.full_clean()
    except ValidationError as validation_error:
        return handle_error(request, validation_error, 403)

    field.save()

    if field_type:
        response = render(request, f"pages/onboarding/form_builder/edit/input_types/{field_type}.html", status=201)
        response["HX-Retarget"] = 'input[data-hx="field_preview_input"]'
        response["HX-Reswap"] = "outerHTML"
        return response

    return HttpResponse(status=201)


def edit_fields_order(request: WebRequest, form_uuid: str) -> HttpResponse:
    # Get the list of field UUIDs from the POST request
    field_uuids = request.POST.getlist("field_uuid")
    print(field_uuids)

    # Get the form to which these fields belong
    form = get_object_or_404(OnboardingForm, uuid=form_uuid)

    # Fetch all the fields in one query
    fields = OnboardingField.objects.filter(uuid__in=field_uuids, form=form)

    # Create a dictionary for UUID to order mapping
    uuid_to_order = {uuid: index + 1 for index, uuid in enumerate(field_uuids)}

    # Update each field's order
    with transaction.atomic():
        for field in fields:
            field.order = uuid_to_order.get(str(field.uuid), 1000)

        if fields:
            OnboardingField.objects.bulk_update(fields, ["order"])

    return HttpResponse(status=204)


def delete_field_endpoint(request: WebRequest, form_uuid: str, field_uuid: str) -> HttpResponse:
    try:
        field = get_valid_form_field(form_uuid, field_uuid, request.actor)
    except OnboardingForm.DoesNotExist:
        return handle_error(request, "Form not found", 404)
    except OnboardingField.DoesNotExist:
        return handle_error(request, "Field not found", 404)

    print(field)
    field.delete()
    print(field)
    return HttpResponse(status=200)


def handle_error(request, error_message, status=404):
    messages.error(request, error_message)
    if request.htmx:
        response = render(request, "base/toast.html")
    else:
        response = HttpResponse(status=status)
    return response
