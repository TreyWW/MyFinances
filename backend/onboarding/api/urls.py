from django.urls import path, include

urlpatterns = [
    path("forms/", include("backend.onboarding.api.forms.urls")),
]

app_name = "onboarding"
