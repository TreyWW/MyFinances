from django.http import HttpResponse
from django.shortcuts import render

from backend.models import Notification
from backend.types.htmx import HtmxHttpRequest


def get_notification_html(request: HtmxHttpRequest):
    user_notifications = Notification.objects.filter(user=request.user).order_by("-date")
    above_5 = False

    if user_notifications.count() > 5:
        user_notifications = user_notifications[:5]
        above_5 = True

    return render(
        request,
        "base/topbar/_notification_dropdown_items.html",
        {"notifications": user_notifications, "notifications_above_max": above_5},
    )


def delete_notification(request: HtmxHttpRequest, id: int):
    notif = Notification.objects.filter(id=id, user=request.user).first()

    if notif is None or notif.user != request.user:
        return HttpResponse(status=404, content="Notification not found")

    notif.delete()

    return HttpResponse(status=200)
