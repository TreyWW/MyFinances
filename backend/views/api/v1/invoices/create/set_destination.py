from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

to_get = ["name", "address", "city", "country"]


@require_http_methods(["POST"])
def set_destination_to(request: HttpRequest):
    context = {}

    context.update({key: request.POST.get(key) for key in to_get})

    return render(request, "pages/invoices/create/_to_destination.html", context)


@require_http_methods(["POST"])
def set_destination_from(request: HttpRequest):
    context = {}

    context.update({key: request.POST.get(key) for key in to_get})

    return render(request, "pages/invoices/create/_from_destination.html", context)
