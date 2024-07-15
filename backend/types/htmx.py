from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from backend.models import User, Organization


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
    user: User
    no_retarget: bool | None


class UnauthorizedHttpRequest(HttpRequest):
    user: AnonymousUser
    htmx: HtmxDetails
    no_retarget: bool | None


class HtmxAnyHttpRequest(HttpRequest):
    user: User | AnonymousUser
    htmx: HtmxDetails
    no_retarget: bool | None
