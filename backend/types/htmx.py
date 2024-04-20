from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django_htmx.middleware import HtmxDetails

from backend.models import User


class HtmxHttpRequest(HttpRequest):
    htmx: HtmxDetails
    user: User


class UnauthorizedHttpRequest(HttpRequest):
    user: AnonymousUser
