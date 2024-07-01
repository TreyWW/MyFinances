from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from backend.models import User, Organization


class WebRequest(HttpRequest):
    user: User
    team: Organization | None
    actor: User | Organization

    htmx: HtmxDetails
    no_retarget: bool | None
