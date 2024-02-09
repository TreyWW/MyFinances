import traceback

from django.http import HttpRequest
from django_ratelimit.exceptions import Ratelimited

from backend.decorators import *
from backend.models import *


def universal(request: HttpRequest, exception=None):
    messages.error(
        request,
        "Sorry, something went wrong on our end! We've contacted our team, please email us if this issue continues.",
    )
    traceback.print_exc()
    exec_error = traceback.format_exc()
    print(f"WAS A TRACEBACK ERROR: EXCEPTION: {exception}")

    if len(exec_error) > 4999:
        return

    if request.user.is_authenticated:
        messages.error(request, "Sorry, something went wrong!")
        TracebackError(user=request.user, error=exec_error).save()
    else:
        TracebackError(error=exec_error).save()

    return redirect("dashboard")


def e_403(request: HttpRequest, exception=None):
    if isinstance(exception, Ratelimited):
        messages.error(
            request,
            "Woah, slow down there. You've been temporarily blocked from this page due to extreme requests.",
        )
        traceback.print_exc()
        exec_error = traceback.format_exc()
        if len(exec_error) < 4999:
            TracebackError(error=exec_error).save()
        return redirect("login")
    else:
        messages.error(
            request,
            "Sorry, something went wrong on our end!"
            "We've contacted our team, please email us if this issue continues.",
        )
        traceback.print_exc()
        exec_error = traceback.format_exc()
        print(f"WAS A TRACEBACK ERROR: EXCEPTION: {exception}")

        if len(exec_error) > 4999:
            return

        if request.user.is_authenticated:
            TracebackError(user=request.user, error=exec_error).save()
        else:
            TracebackError(error=exec_error).save()

        return redirect("dashboard")
