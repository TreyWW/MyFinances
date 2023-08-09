from django.http import HttpResponse, HttpRequest, HttpResponseBadRequest, HttpResponseForbidden, \
    HttpResponseServerError
from django.shortcuts import render, redirect

from django.contrib.auth import get_user_model

User = get_user_model()


def index(request: HttpRequest):
    return render(request, 'core/pages/index.html')