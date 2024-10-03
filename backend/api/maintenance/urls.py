from django.urls import path

from . import now

urlpatterns = [
    path("cleanup/", now.handle_maintenance_now_endpoint, name="cleanup"),
]

app_name = "maintenance"
