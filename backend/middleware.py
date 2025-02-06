from django.contrib.auth.models import AnonymousUser
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user
from django.db import connection, OperationalError
from django.http import HttpResponse

from backend.models import User
from backend.core.types.htmx import HtmxAnyHttpRequest
from backend.core.types.requests import WebRequest


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/api/hc/healthcheck/":
            try:
                status = connection.ensure_connection()
            except OperationalError:
                status = "error"

            if not status:  # good
                return HttpResponse(status=200, content="All operations are up and running!")
            return HttpResponse(status=503, content="Service Unavailable")
        return self.get_response(request)


class HTMXPartialLoadMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HtmxAnyHttpRequest):
        response: HttpResponse = self.get_response(request)

        if hasattr(response, "retarget"):
            response.headers["HX-Retarget"] = response.retarget
        elif request.htmx.boosted and not response.headers.get("HX-Retarget") and not hasattr(response, "no_retarget"):
            response.headers["HX-Retarget"] = "#main_content"
            response.headers["HX-Reswap"] = "innerHTML"
            # if 'data-layout="breadcrumbs"' not in str(response.content):
            response.headers["HX-Trigger"] = "update_breadcrumbs"

        # fix issue with browser not rendering CSS when you use the back function issue #468
        if "HX-Request" in request.headers:
            response["Cache-Control"] = "no-store, max-age=0"
        return response


class LastVisitedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == "GET" and "text/html" in request.headers.get("Accept", ""):
            try:
                request.session["last_visited"] = request.session["currently_visiting"]
            except KeyError:
                pass
            current_url = request.build_absolute_uri()
            request.session["currently_visiting"] = current_url
        return self.get_response(request)


class CustomUserMiddleware(MiddlewareMixin):
    def process_request(self, request: WebRequest):
        user = get_user(request)

        # Replace request.user with CustomUser instance if authenticated
        if user.is_authenticated:
            request.user = User.objects.get(pk=user.pk)
            request.team = request.user.logged_in_as_team or None
            request.team_id = request.team.id if request.team else None
            request.actor = request.team or request.user
        else:
            # If user is not authenticated, set request.user to AnonymousUser
            request.user = AnonymousUser()  # type: ignore[assignment]
            request.actor = request.user
