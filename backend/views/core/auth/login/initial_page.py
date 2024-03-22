from django.http import HttpRequest
from django.views.decorators.http import require_GET

from backend.decorators import *
from settings.settings import (
    SOCIAL_AUTH_GITHUB_ENABLED,
    SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
)


@require_GET
@not_authenticated
def login_initial_page(request: HttpRequest):
    next_page = request.GET.get("next")  # This just gets carried over for next step

    return render(
        request,
        "pages/auth/login_initial.html",
        {
            "github_enabled": SOCIAL_AUTH_GITHUB_ENABLED,
            "google_enabled": SOCIAL_AUTH_GOOGLE_OAUTH2_ENABLED,
            "next": next_page,
        },
    )
