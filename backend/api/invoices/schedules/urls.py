from django.urls import path

from . import delete, fetch, create, receive

urlpatterns = [
    path("schedules/receive/", receive.receive_scheduled_invoice, name="receive"),
    path("create_schedule/", create.create_schedule, name="create"),
    path("schedules/onetime/<str:schedule_id>/cancel/", delete.cancel_onetime_schedule, name="onetime cancel"),
    path("schedules/onetime/fetch/<str:invoice_id>/", fetch.fetch_onetime_schedules, name="onetime fetch"),
]

app_name = "schedules"
