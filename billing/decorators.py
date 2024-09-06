from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse

from billing.service.entitlements import has_entitlement, get_entitlements


def has_entitlements_called_from_backend_handler(entitlements: list[str] | str, htmx_api: bool = False):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            user_does_have_entitlements: bool
            if isinstance(entitlements, (list, set)):
                users_entitlements = get_entitlements(request.actor)
                user_does_have_entitlements = all(entitlement in users_entitlements for entitlement in entitlements)
            else:
                user_does_have_entitlements = has_entitlement(request.actor, entitlements)

            if user_does_have_entitlements:
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, f"Your plan unfortunately doesn't include this feature.")

                if htmx_api:
                    return render(request, "base/toast.html", {"autohide": False})
                elif request.htmx:
                    return HttpResponseRedirect(reverse("billing:dashboard"))
                return redirect("billing:dashboard")

        return wrapper_func

    return decorator
