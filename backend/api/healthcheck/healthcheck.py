from django.db import connection, OperationalError
from django.http import HttpRequest, HttpResponse
from login_required import login_not_required


@login_not_required
def ping(request: HttpRequest) -> HttpResponse:
    return HttpResponse("pong")


@login_not_required
def healthcheck(request: HttpRequest) -> HttpResponse:
    try:
        connection.ensure_connection()
        return HttpResponse(status=200, content="All operations are up and running!")
    except OperationalError:
        return HttpResponse(status=503, content="Service Unavailable")
