from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

INFO = openapi.Info(
    title="MyFinances Public API",
    default_version="v0.0.1",
    description="",
    terms_of_service="",
    contact=openapi.Contact(email="support@strelix.org"),
    license=openapi.License(name="AGPL v3"),
)

schema_view = get_schema_view(
    INFO,
    public=True,
    permission_classes=[permissions.AllowAny],
)


def get_swagger_ui():
    return schema_view


def get_swagger_endpoints(debug):
    return (
        [
            path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
        ]
        + [
            path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
            path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
        ]
        if debug
        else []
    )


TEAM_PARAMETER = openapi.Parameter(
    "team_id", openapi.IN_QUERY, description="id of the team you want to do this action under", type=openapi.TYPE_STRING, required=False
)
