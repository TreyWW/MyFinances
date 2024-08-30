from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path as url
from django.views.generic import RedirectView
from django.views.static import serve

from backend.api.public.swagger_ui import get_swagger_ui, get_swagger_endpoints
from backend.views.core import receipts
from backend.views.core.invoices.single.view import view_invoice_with_uuid_endpoint
from backend.views.core.other.index import dashboard
from backend.views.core.other.index import index
from backend.views.core.quotas.view import quotas_list
from backend.views.core.quotas.view import quotas_page
from backend.views.core.quotas.view import view_quota_increase_requests
from settings.settings import BILLING_ENABLED

url(
    r"^frontend/static/(?P<path>.*)$",
    serve,
    {"document_root": settings.STATICFILES_DIRS[0]},
)
urlpatterns = [
    path("tz_detect/", include("tz_detect.urls")),
    path("api/", include("backend.api.urls")),
    path("webhooks/", include("backend.webhooks.urls")),
    path("", index, name="index"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/settings/", include("backend.views.core.settings.urls")),
    path("dashboard/teams/", include("backend.views.core.teams.urls")),
    path("dashboard/invoices/", include("backend.views.core.invoices.urls")),
    path("dashboard/quotas/", quotas_page, name="quotas"),
    path("dashboard/quotas/<str:group>/", quotas_list, name="quotas group"),
    path("dashboard/emails/", include("backend.views.core.emails.urls")),
    path("dashboard/admin/quota_requests/", view_quota_increase_requests, name="admin quota increase requests"),
    path("dashboard/file_storage/", include("backend.views.core.file_storage.urls")),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path(
        "dashboard/receipts/",
        receipts.dashboard.receipts_dashboard,
        name="receipts dashboard",
    ),
    path(
        "invoice/<str:uuid>",
        view_invoice_with_uuid_endpoint,
        name="invoices view invoice",
    ),
    path("login/external/", include("social_django.urls", namespace="social")),
    path("auth/", include("backend.views.core.auth.urls")),
    path("dashboard/clients/", include("backend.views.core.clients.urls")),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # may not need to be in debug
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if BILLING_ENABLED:
    urlpatterns.append(path("", include("billing.urls")))

schema_view = get_swagger_ui()
urlpatterns += get_swagger_endpoints(settings.DEBUG)

handler500 = "backend.views.core.other.errors.universal"
handler404 = "backend.views.core.other.errors.universal"
handler403 = "backend.views.core.other.errors.e_403"
