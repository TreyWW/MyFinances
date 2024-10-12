from django.urls import path

from backend.core.views.settings.view import change_password, view_settings_page_endpoint

urlpatterns = [
    path("", view_settings_page_endpoint, name="dashboard"),
    path("<str:page>/", view_settings_page_endpoint, name="dashboard with page"),
    path(
        "profile/change_password/",
        change_password,
        name="change_password",
    ),
]

app_name = "settings"
