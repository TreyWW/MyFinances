from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import render
from backend.utils import Modals

# Still working on


def open_modal(request: HttpRequest, modal_name, context_type=None, context_value=None):
    try:
        template_name = f"modals/{modal_name}.html"
        return render(request, template_name)
    except:
        return HttpResponseBadRequest("Something went wrong")
