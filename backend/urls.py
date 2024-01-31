from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import re_path as url, path, include
from django.views.static import serve

from backend.views.core import (
    other,
    passwords,
    settings as settings_v,
    invoices,
    clients,
    receipts,
)
from backend.views.core.currency_converter import dashboard as cc_dashboard
from backend.views.core.other.index import index, dashboard
from .views.core.invoices import edit

url(
    r"^frontend/static/(?P<path>.*)$",
    serve,
    {"document_root": settings.STATICFILES_DIRS[0]},
)

urlpatterns = [
    path("api/v1/", include("backend.api.urls")),
    path("api/external/", include("restAPI.urls")),
    path("", index, name="index"),
    path("dashboard", dashboard, name="dashboard"),
    path("dashboard/settings/", settings_v.view.settings_page, name="user settings"),
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
        "dashboard/settings/teams/create",
        settings_v.teams.create_team,
        name="user settings teams create",
    ),
    path(
        "dashboard/settings/teams/invite",
        settings_v.teams.invite_user_to_team,
        name="user settings teams invite",
    ),
    path(
        "dashboard/settings/teams/join/<str:code>",
        settings_v.teams.join_team_page,
        name="user settings teams join",
    ),
    path(
        "dashboard/settings/teams/join/<str:code>/accept/",
        settings_v.teams.join_team_accepted,
        name="user settings teams join accept",
    ),
    path(
        "dashboard/settings/teams/join/<str:code>/decline/",
        settings_v.teams.join_team_declined,
        name="user settings teams join decline",
    ),
    path(
        "dashboard/settings/teams/leave/",
        settings_v.teams.leave_team,
        name="user settings teams join leave",
    ),
    path(
        "dashboard/settings/teams/leave/confirm",
        settings_v.teams.leave_team_confirm,
        name="user settings teams join leave confirm",
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
        "dashboard/invoices/",
        invoices.dashboard.invoices_dashboard,
        name="invoices dashboard",
    ),
    path(
        "dashboard/invoices/access/<str:id>",
        invoices.manage_access.manage_access,
        name="invoices dashboard manage_access",
    ),
    path(
        "dashboard/invoices/access/<str:id>/create",
        invoices.manage_access.create_code,
        name="invoices dashboard manage_access create",
    ),
    path(
        "dashboard/invoices/access/<str:id>/delete",
        invoices.manage_access.delete_code,
        name="invoices dashboard manage_access delete",
    ),
    path(
        "dashboard/invoices/preview/<str:id>",
        invoices.view.preview,
        name="invoices dashboard preview",
    ),
    path(
        "invoice/<str:uuid>",
        invoices.view.view,
        name="invoices view invoice",
    ),
    path(
        "dashboard/invoices/create/",
        invoices.create.create_invoice_page,
        name="invoices dashboard create",
    ),
    # path(
    #    "dashboard/invoices/<str:id>",
    #    invoices.dashboard.invoices_dashboard_id,
    #    name="invoices dashboard edit",
    # ),
    path(
        "dashboard/invoices/edit/<str:id>",
        invoices.edit.edit_invoice_page,
        # invoices.edit.invoice_edit_page_get,
        name="invoices dashboard edit",
    ),
    # path('dashboard/invoices/<str:id>/edit', invoices.dashboard.invoices_dash~board_id, name='invoices dashboard'),
    path("login/external/", include("social_django.urls", namespace="social")),
    path("login/", other.login.login_page, name="login"),
    path("logout/", other.login.logout_view, name="logout"),
    # path('logout_test/', other.login.logout_view, name='logout_test'),
    path(
        "login/create_account",
        other.login.CreateAccountChooseView.as_view(),
        name="login create_account",
    ),
    path(
        "login/create_account/manual",
        other.login.CreateAccountManualView.as_view(),
        name="login create_account manual",
    ),
    path(
        "login/forgot_password",
        other.login.forgot_password_page,
        name="login forgot_password",
    ),
    path(
        "login/reset-password/",
        passwords.generate.password_reset,
        name="user set password reset",
    ),
    path(
        "login/set-password/<str:secret>",
        passwords.view.set_password,
        name="user set password",
    ),
    path(
        "login/set-password/<str:secret>/set",
        passwords.set.set_password_set,
        name="user set password set",
    ),
    path(
        "admin/generate-password",
        passwords.generate.set_password_generate,
        name="admin set password generate",
    ),
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
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]
    )

handler500 = "backend.views.core.other.errors.universal"
handler404 = "backend.views.core.other.errors.universal"
handler403 = "backend.views.core.other.errors.e_403"
