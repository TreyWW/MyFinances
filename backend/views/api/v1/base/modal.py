from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import render
from backend.utils import Modals

# Still working on


def open_modal(request: HttpRequest, modal_name):
    context = {"modals": []}

    try:
        modal_function = getattr(Modals, modal_name)
        context["modals"].append(modal_function())
    except AttributeError:
        print("Failed to find modal function")
        return HttpResponseBadRequest("Failed to find modal")

    return render(request, "core/components/modal.html", context)
