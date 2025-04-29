from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import render

from backend.models import Notification
from backend.core.types.htmx import HtmxHttpRequest


def get_notification_html(request: HtmxHttpRequest):
    user_notifications = Notification.objects.filter(user=request.user).order_by("-date")
    count = user_notifications.count()

    if count > 5:
        user_notifications = user_notifications[:5]

    return render(
        request,
        "base/topbar/_notification_dropdown_items.html",
        {"notifications": user_notifications, "notif_count": count},
    )


def get_notification_count_html(request: HtmxHttpRequest):
    user_notifications = Notification.objects.filter(user=request.user).count()
    return HttpResponse(f"{user_notifications}")


def delete_notification(request: HtmxHttpRequest, id: int):
    notif = Notification.objects.filter(id=id, user=request.user).first()

    if notif is None or notif.user != request.user:
        if request.htmx:
            messages.error(request, "Notification not found")
            return render(request, "base/toasts.html")
        return HttpResponse(status=404, content="Notification not found")

    notif.delete()

    response = HttpResponse(status=200)
    response["HX-Trigger"] = "refresh_notification_count"
    return response
