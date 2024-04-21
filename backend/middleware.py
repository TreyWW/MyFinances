from django.db import connection, OperationalError
from django.http import HttpResponse

from backend.types.htmx import HtmxAnyHttpRequest


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
        response = self.get_response(request)
        if request.htmx.boosted:
            response.headers["HX-Retarget"] = "#main_content"
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
