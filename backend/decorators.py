from functools import wraps

from django.contrib import messages

from django.shortcuts import redirect


def not_authenticated(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard")
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def staff_only(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_staff and request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You don't have permission to view this page.")
            return redirect("dashboard")

    return wrapper_func


def superuser_only(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You don't have permission to view this page.")
            return redirect("dashboard")

    return wrapper_func


def customer_only(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_customer:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "You don't have permission to view this page as you are not on a customer account.")
            return redirect("dashboard")

    return wrapper_func


def not_customer(view_func):
    @wraps(view_func)
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_customer:
            messages.error(request, "You don't have permission to view this page as you are on a customer account.")
            return redirect("index")  # not yet created view
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


# Aliases

not_logged_in = not_authenticated
logged_out = not_authenticated
