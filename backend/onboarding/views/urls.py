from django.urls import path, include

urlpatterns = [
    path("forms/", include("backend.onboarding.views.forms.urls")),
]

app_name = "onboarding"
