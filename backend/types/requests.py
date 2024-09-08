from typing import Any

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from backend.models import User, Organization


class WebRequest(HttpRequest):
    user: User
    team: Organization | None
    team_id: int | None
    actor: User | Organization

    users_subscription: Any | None

    htmx: HtmxDetails
    no_retarget: bool | None
