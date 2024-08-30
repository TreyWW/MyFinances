from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from login_required import login_not_required

from backend.types.requests import WebRequest


@login_not_required
@csrf_exempt
def stripe_listener_webhook_endpoint(request: WebRequest):
    print("It called the WH!")
    print(request)
    print(request.GET)
    print(request.POST)
    return HttpResponse(status=200)
