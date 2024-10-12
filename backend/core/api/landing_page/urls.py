from django.urls import path
from . import email_waitlist

urlpatterns = [
    path("join_waitlist/", email_waitlist.join_waitlist_endpoint, name="join_waitlist"),
]

app_name = "landing_page"
