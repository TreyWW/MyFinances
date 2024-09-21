from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from backend.models import User
from backend.templatetags.feature_enabled import feature_enabled
from backend.utils.dataclasses import BaseServiceResponse


class MagicLinkLoginServiceResponse(BaseServiceResponse[None]): ...


def magic_link_login_service(request, email) -> MagicLinkLoginServiceResponse:
    if not feature_enabled("areMagicLinkLoginsAllowed"):
        return MagicLinkLoginServiceResponse(False, error_message="Magic links are currently not available, please login manually")

    if not email:
        return MagicLinkLoginServiceResponse(False, error_message="Please enter an email address")

    try:
        validate_email(email)
    except ValidationError:
        return MagicLinkLoginServiceResponse(False, error_message="Please enter a valid email address")

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return MagicLinkLoginServiceResponse(False, error_message="This email address is not registered")

    if not user.is_active:
        return MagicLinkLoginServiceResponse(False, error_message="This account is inactive")

    # user.
