from dataclasses import dataclass
from typing import Literal

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from django.contrib import messages


@dataclass(frozen=True, slots=True)
class ToastMessage:
    message: str = ""
    type: Literal["success", "error"] = "error"


def render_toast_message(request: HttpRequest, message: ToastMessage = None) -> HttpResponse:
    if message:
        if message.type == "success":
            messages.success(request, message.message)
        else:
            messages.error(request, message.message)
    return render(request, "base/toasts.html")  # htmx will handle the toast
