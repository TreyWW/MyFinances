import traceback
from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django_ratelimit.exceptions import Ratelimited
from backend.decorators import *
from backend.utils import Notification, Toast
import json
from backend.models import *

from django.contrib.auth import get_user_model, logout


def universal(request: HttpRequest, exception=None):
    messages.error(request,
                   "Sorry, something went wrong on our end! We've contacted our team, please email us if this issue continues.")
    traceback.print_exc()
    exec_error = traceback.format_exc()
    print(f"WAS A TRACEBACK ERROR: EXCEPTION: {exception}")

    if len(exec_error) > 4999: return

    if request.user.is_authenticated:
        Toast(request=request, title="Error", message="Sorry, something went wrong!", autohide=False, level="danger")
        TracebackErrors(user=request.user, error=exec_error).save()
    else:
        TracebackErrors(error=exec_error).save()

    return redirect('dashboard')


def e_403(request: HttpRequest, exception=None):
    if isinstance(exception, Ratelimited):
        messages.error(request,
                       "Woah, slow down there. You've been temporarily blocked from this page due to extreme requests.")
        traceback.print_exc()
        exec_error = traceback.format_exc()
        if len(exec_error) < 4999:
            TracebackErrors(error=exec_error).save()
        return redirect("login")
    else:
        Toast(request=request,title="Error", message="Sorry, something went wrong!", autohide=False, level="danger")
        messages.error(request,
                       "Sorry, something went wrong on our end!"
                       "We've contacted our team, please email us if this issue continues.")
        traceback.print_exc()
        exec_error = traceback.format_exc()
        print(f"WAS A TRACEBACK ERROR: EXCEPTION: {exception}")

        if len(exec_error) > 4999: return

        if request.user.is_authenticated:
            TracebackErrors(user=request.user, error=exec_error).save()
        else:
            TracebackErrors(error=exec_error).save()

        return redirect('dashboard')
    return redirect('dashboard')
