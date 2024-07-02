from backend.models import User, Organization
from backend.views.core.onboarding.models import OnboardingForm


def create_onboarding_form(actor: User | Organization) -> OnboardingForm:
    form = OnboardingForm.objects.create(title=f"{actor}'s Untitled Form", owner=actor)

    return form
