from django.urls import path
from . import kick

urlpatterns = [
    path(
        "kick/<int:user_id>",
        kick.kick_user,
        name="kick",
    ),
]

app_name = "teams"
