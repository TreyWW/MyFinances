from django.urls import path

from . import api_keys

urlpatterns = [
    path(
        "api_keys/generate/",
        api_keys.generate_api_key,
        name="api-keys generate",
    ),
]

app_name = "admin"
