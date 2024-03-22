from django.contrib.auth import login, authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpRequest
from django.urls import resolve
from django.urls.exceptions import Resolver404
from django.views.decorators.http import require_POST

from backend.decorators import *
from settings.helpers import ARE_EMAILS_ENABLED
from .helpers import render_toast_message, ToastMessage


@not_authenticated
@require_POST
def login_manual(request: HttpRequest):  # HTMX POST
    if not request.htmx:
        return redirect("auth:login")
    email = request.POST.get("email")
    password = request.POST.get("password")
    page = str(request.POST.get("page"))
    next_page = request.POST.get("next")

    if not page or page == "1":
        return render(
            request,
            "pages/auth/login.html",
            context={"email": email, "next": next_page, "magic_links_enabled": ARE_EMAILS_ENABLED},
        )

    if not email:
        return render_toast_message(request, ToastMessage("Please enter an email"))

    try:
        validate_email(email)
    except ValidationError:
        return render_toast_message(request, ToastMessage("Please enter a valid email"))

    if not password:
        return render_toast_message(request, ToastMessage("Please enter a password"))

    user = authenticate(request, username=email, password=password)

    if not user:
        return render_toast_message(request, ToastMessage("Incorrect email or password"))

    login(request, user)
    messages.success(request, "Successfully logged in")

    response = HttpResponse(request, status=200)

    try:
        resolve(next_page)
        response["HX-Location"] = next_page
    except Resolver404:
        print(f"Did not resolve: {next_page}")  # this is fine, just means user will not be redirected due to CSRF

    return response
