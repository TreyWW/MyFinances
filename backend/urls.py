from __future__ import annotations

from core.views.other.index import dashboard
from core.views.other.index import index, pricing
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path as url
from django.views.generic import RedirectView
from django.views.static import serve

from backend.finance.views.invoices.single.view import view_invoice_with_uuid_endpoint
from backend.finance.views.receipts.dashboard import receipts_dashboard

# from core.views.quotas.view import quotas_list
# from core.views.quotas.view import view_quota_increase_requests

url(
    r"^frontend/static/(?P<path>.*)$",
    serve,
    {"document_root": settings.STATICFILES_DIRS[0]},
)

api_patterns = [path("finance/", include("backend.finance.api"))]

urlpatterns = [
    path("", include(("core.urls", "core"), namespace="core")),
    path("webhooks/", include("backend.webhooks.urls")),
    path("", index, name="index"),
    path("pricing", pricing, name="pricing"),
    path("dashboard/", dashboard, name="dashboard"),
    path("dashboard/", include("backend.finance.views.urls")),
    # path("dashboard/quotas/", quotas_page, name="quotas"),
    path("dashboard/quotas/", RedirectView.as_view(url="/dashboard"), name="quotas"),
    # path("dashboard/quotas/<str:group>/", quotas_list, name="quotas group"),
    path("dashboard/reports/", include("backend.finance.views.reports.urls")),
    # path("dashboard/admin/quota_requests/", view_quota_increase_requests, name="admin quota increase requests"),
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
    path("api/", include("backend.api.urls", namespace="api")),
    # path("api/", include("core.api.urls", namespace="api"))
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if getattr(settings, "BILLING_ENABLED"):
    urlpatterns.append(path("", include(("billing.urls", "billing"), namespace="billing")))

handler500 = "core.views.other.errors.universal"
handler404 = "core.views.other.errors.universal"
handler403 = "core.views.other.errors.e_403"
