from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import render
from backend.utils import Modals

# Still working on


def open_modal(request: HttpRequest, modal_name):
    context = {"modals": []}

    try:
        modal_function = getattr(Modals, modal_name)
    except AttributeError:
        print("Failed to find modal function")
        return HttpResponseBadRequest("Failed to find modal")

    # Extract parameters that start with capital "P"
    modal_params = {}
    for param, value in request.GET.items():
        if param.startswith("P"):
            modal_params[param[1:]] = value  # Remove the 'P' prefix

    # Call the modal function with the extracted parameters
    modal_instance = modal_function(**modal_params)

    context["modals"].append(modal_instance)

    return render(request, "core/components/modal.html", context)
