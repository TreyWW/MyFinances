from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path as url
from django.views.generic import RedirectView
from django.views.static import serve

from backend.core.api.public.swagger_ui import get_swagger_ui, get_swagger_endpoints
from backend.finance.views.invoices.single.view import view_invoice_with_uuid_endpoint
from backend.finance.views.receipts.dashboard import receipts_dashboard
from backend.core.views.other.index import dashboard
from backend.core.views.other.index import index, pricing
from backend.core.views.quotas.view import quotas_list
from backend.core.views.quotas.view import view_quota_increase_requests
from settings.settings import BILLING_ENABLED

url(
    r"^frontend/static/(?P<path>.*)$",
    serve,
    {"document_root": settings.STATICFILES_DIRS[0]},
)
urlpatterns = [
    path("tz_detect/", include("tz_detect.urls")),
    path("webhooks/", include("backend.core.webhooks.urls")),
    path("", index, name="index"),
    path("pricing", pricing, name="pricing"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/settings/", include("backend.core.views.settings.urls")),
    path("dashboard/teams/", include("backend.core.views.teams.urls")),
    path("dashboard/", include("backend.finance.views.urls")),
    # path("dashboard/quotas/", quotas_page, name="quotas"),
    path("dashboard/quotas/", RedirectView.as_view(url="/dashboard"), name="quotas"),
    path("dashboard/quotas/<str:group>/", quotas_list, name="quotas group"),
    path("dashboard/emails/", include("backend.core.views.emails.urls")),
    path("dashboard/reports/", include("backend.finance.views.reports.urls")),
    path("dashboard/admin/quota_requests/", view_quota_increase_requests, name="admin quota increase requests"),
    path("dashboard/file_storage/", include("backend.storage.views.urls")),
    path("dashboard/clients/", include("backend.clients.views.urls")),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path(
        "dashboard/receipts/",
        receipts_dashboard,
        name="receipts dashboard",
    ),
    path(
        "invoice/<str:uuid>",
        view_invoice_with_uuid_endpoint,
        name="invoices view invoice",
    ),
    path("login/external/", include("social_django.urls", namespace="social")),
    path("auth/", include("backend.core.views.auth.urls")),
    path("api/", include("backend.core.api.urls")),
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

handler500 = "backend.core.views.other.errors.universal"
handler404 = "backend.core.views.other.errors.universal"
handler403 = "backend.core.views.other.errors.e_403"
