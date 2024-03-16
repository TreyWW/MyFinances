from django.db import connection, OperationalError
from django.http import HttpResponse


class HealthCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/api/hc/healthcheck/':
            try:
                status = connection.ensure_connection()
            except OperationalError:
                status = "error"

            if not status:  # good
                return HttpResponse(status=200, content="All operations are up and running!")
            return HttpResponse(status=503, content="Service Unavailable")
        return self.get_response(request)
