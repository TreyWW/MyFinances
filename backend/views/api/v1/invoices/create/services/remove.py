from django.http import HttpRequest, JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(['DELETE'])
def remove_service(request: HttpRequest):
    return HttpResponse('')
