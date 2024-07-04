from django.db.models import QuerySet

from backend.models import User, Organization
from backend.views.core.onboarding.models import OnboardingForm, OnboardingField


def validate_page(page: str | None, sub_page: str | None) -> bool:
    return (not page or page in ["profile", "form-builder", "api_keys"]) and (not sub_page or sub_page in ["list", "edit"])


def get_existing_forms(actor: User | Organization) -> QuerySet[OnboardingForm]:
    return OnboardingForm.filter_by_owner(owner=actor)


def get_form(uuid, actor: User | Organization) -> OnboardingForm:
    return get_existing_forms(actor).get(uuid=uuid)


def get_valid_form(uuid, actor: User | Organization) -> OnboardingForm:
    # may do extra logic at a later point
    return get_form(uuid, actor)


def get_valid_form_field(form_uuid, field_uuid, actor: User | Organization) -> OnboardingField:
    """
    :raises: OnboardingField.DoesNotExist
    :return: OnboardingField
    """
    form = get_valid_form(form_uuid, actor)
    return form.fields.get(uuid=field_uuid)
