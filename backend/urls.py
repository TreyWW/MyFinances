from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from django.urls import re_path as url
from django.views.generic import RedirectView
from django.views.static import serve

from backend.views.core import clients
from backend.views.core import invoices
from backend.views.core import receipts
from backend.views.core import settings as settings_v
from backend.views.core.currency_converter import dashboard as cc_dashboard
from backend.views.core.invoices.overview import manage_invoice
from backend.views.core.other.index import dashboard
from backend.views.core.other.index import index
from backend.views.core.quotas.view import quotas_list
from backend.views.core.quotas.view import quotas_page
from backend.views.core.quotas.view import view_quota_increase_requests

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
    path("dashboard/settings/", settings_v.view.settings_page, name="user settings"),
    path("dashboard/invoices/", include("backend.views.core.invoices.urls")),
    path("dashboard/quotas/", quotas_page, name="quotas"),
    path("dashboard/quotas/<str:group>/", quotas_list, name="quotas group"),
    path("dashboard/emails/", include("backend.views.core.emails.urls")),
    path("dashboard/admin/quota_requests/", view_quota_increase_requests, name="admin quota increase requests"),
    path(
        "dashboard/invoice/<str:invoice_id>/",
        manage_invoice,
        name="invoice overview",
    ),
    path("favicon.ico", RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico")),
    path(
        "dashboard/settings/teams",
        settings_v.teams.teams_dashboard,
        name="user settings teams",
    ),
    path(
        "dashboard/settings/teams/permissions/",
        settings_v.teams.manage_permissions_dashboard,
        name="user settings teams permissions",
    ),
    path(
        "dashboard/profile/change_password/",
        settings_v.view.change_password,
        name="user settings change_password",
    ),
    path(
        "dashboard/receipts/",
        receipts.dashboard.receipts_dashboard,
        name="receipts dashboard",
    ),
    path(
        "invoice/<str:uuid>",
        invoices.view.view,
        name="invoices view invoice",
    ),
    path("login/external/", include("social_django.urls", namespace="social")),
    path("auth/", include("backend.views.core.auth.urls")),
    path(
        "dashboard/clients/",
        clients.dashboard.clients_dashboard,
        name="clients dashboard",
    ),
    path(
        "dashboard/clients/create/",
        clients.create.create_client,
        name="clients create",
    ),
    path(
        "dashboard/currency_converter/",
        cc_dashboard.currency_convert_view,
        name="currency converter",
    ),
    path("admin/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        url(r"^__debug__/", include(debug_toolbar.urls)),
    ]

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # may not need to be in debug
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

handler500 = "backend.views.core.other.errors.universal"
handler404 = "backend.views.core.other.errors.universal"
handler403 = "backend.views.core.other.errors.e_403"
