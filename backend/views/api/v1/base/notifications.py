from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from backend.models import Notification


def get_notification_html(request: HttpRequest):
    user_notifications = Notification.objects.filter(user=request.user)
    notifications_normal = user_notifications.filter(action="normal")
    notifications_redirect = user_notifications.filter(action="redirect")
    notifications_modal = user_notifications.filter(action="modal")
    modals = []

    # TODO: Make modals have their own actual modal that gets loaded ALSO VIA HTMX
    # TODO: e.g. https://htmx.org/examples/modal-bootstrap/
    # for modal in notifications_modal:
    #     modals.append({
    #
    #     })

    return render(
        request,
        "core/partials/base/_notification_dropdown_items.html",
        {
            "notifications": {
                "normal": notifications_normal,
                "modal": notifications_modal,
                "redirect": notifications_redirect,
            }
        },
    )


def delete_notification(request: HttpRequest, id: int):
    notif = Notification.objects.filter(id=id).first()

    if notif is None or notif.user != request.user:
        return HttpResponse(status=404, content="Notification not found")

    notif.delete()

    return HttpResponse(status=200)
