from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from backend.models import Notification


def get_notification_html(request: HttpRequest):
    user_notifications = Notification.objects.filter(user=request.user).order_by(
        "-date"
    )[:5]

    return render(
        request,
        "base/topbar/_notification_dropdown_items.html",
        {"notifications": user_notifications},
    )


def delete_notification(request: HttpRequest, id: int):
    notif = Notification.objects.filter(id=id, user=request.user).first()

    if notif is None or notif.user != request.user:
        return HttpResponse(status=404, content="Notification not found")

    notif.delete()

    return HttpResponse(status=200)
