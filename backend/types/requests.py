from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from backend.models import User, Organization


class WebRequest(HttpRequest):
    user: User | AnonymousUser
    team: Organization | None
    actor: User | AnonymousUser | Organization

    htmx: HtmxDetails
    no_retarget: bool | None
