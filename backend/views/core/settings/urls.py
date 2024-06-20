from django.urls import include
from django.urls import path
from django.views.generic import RedirectView

from backend.views.core import settings

urlpatterns = [
    path("", settings.view.default_settings_page_redirect_endpoint, name="dashboard"),
    path("<str:page>/", settings.view.view_settings_page_endpoint, name="dashboard with page"),
    path(
        "profile/change_password/",
        settings.view.change_password,
        name="change_password",
    ),
]

app_name = "settings"
