from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import render

from backend.models import UserSettings, Receipt
from backend.utils import Modals

# Still working on


def open_modal(request: HttpRequest, modal_name, context_type=None, context_value=None):
    try:
        context = {}
        template_name = f"modals/{modal_name}.html"
        if context_type and context_value:
            if context_type == "profile_picture":
                try:
                    context["users_profile_picture"] = UserSettings.objects.get(
                        user=request.user
                    ).profile_picture_url
                except UserSettings.DoesNotExist:
                    pass
        return render(request, template_name, context)
    except:
        return HttpResponseBadRequest("Something went wrong")
