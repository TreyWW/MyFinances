from django.db.models import QuerySet

from backend.models import UserSettings, User, Organization
from backend.views.core.onboarding.models import OnboardingForm


def validate_page(page: str | None, sub_page: str | None) -> bool:
    return (not page or page in ["profile", "form-builder", "api_keys"]) and (not sub_page or sub_page in ["list", "edit"])


def get_existing_forms(actor: User | Organization) -> QuerySet[OnboardingForm]:
    return OnboardingForm.filter_by_owner(owner=actor)


def get_form(uuid, actor: User | Organization) -> OnboardingForm:
    return get_existing_forms(actor).get(uuid=uuid)


def get_valid_form(uuid, actor: User | Organization) -> OnboardingForm:
    form = get_form(uuid, actor)
    return form
