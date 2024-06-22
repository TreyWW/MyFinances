from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from backend.models import User, Team


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
    user: User
    team: Team | None


class UnauthorizedHttpRequest(HttpRequest):
    user: AnonymousUser
    htmx: HtmxDetails
    team: Team | None


class HtmxAnyHttpRequest(HttpRequest):
    user: User | AnonymousUser
    htmx: HtmxDetails
    team: Team | None
