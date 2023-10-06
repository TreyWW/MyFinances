from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path as url
from django.urls import path, include

from backend.views.core import (
    other,
    passwords,
    settings as settings_v,
    invoices,
    clients,
    receipts,
)
from backend.views.core.other.index import index, dashboard
from backend.views.api import v1
from django.contrib import admin

# from backend.views.core.api.v1.user import settings


url(
    r"^frontend/static/(?P<path>.*)$",
    serve,
    {"document_root": settings.STATICFILES_DIRS[0]},
)

urlpatterns = [
    path("", index, name="index"),
    path("dashboard", dashboard, name="dashboard"),
    path("dashboard/settings/", settings_v.view.settings_page, name="user settings"),
    path(
        "dashboard/settings/teams",
        settings_v.teams.teams_dashboard,
        name="user settings teams",
    ),
    path(
        "dashboard/settings/teams/kick/<id:user_id>",
        settings_v.teams.kick_user,
        name="user settings teams",
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
        "dashboard/receipts",
        receipts.dashboard.receipts_dashboard,
        name="receipts dashboard",
    ),
    path(
        "api/v1/receipts/delete/<int:id>",
        v1.receipts.delete.receipt_delete,
        name="api v1 receipts delete",
    ),
    path(
        "api/v1/receipts/new",
        v1.receipts.new.receipt_create,
        name="api v1 receipts new",
    ),
    path(
        "api/v1/base/notifications/get",
        v1.base.notifications.get_notification_html,
        name="api v1 base notifications get",
    ),
    path(
        "api/v1/base/notifications/delete/<int:id>",
        v1.base.notifications.delete_notification,
        name="api v1 base notifications delete",
    ),
    path(
        "dashboard/invoices/",
        invoices.dashboard.invoices_dashboard,
        name="invoices dashboard",
    ),
    path(
        "dashboard/invoices/create/",
        invoices.create.create_invoice_page,
        name="invoices dashboard create",
    ),
    path(
        "dashboard/invoices/<str:id>",
        invoices.dashboard.invoices_dashboard_id,
        name="invoices dashboard edit",
    ),
    # path('dashboard/invoices/<str:id>/edit', invoices.dashboard.invoices_dashboard_id, name='invoices dashboard'),
    path("login/external/", include("social_django.urls", namespace="social")),
    path(
        "api/v1/invoices/create/add_service",
        v1.invoices.create.services.add.add_service,
        name="api v1 invoices create services add",
    ),
    path(
        "api/v1/invoices/create/remove_service",
        v1.invoices.create.services.remove.remove_service,
        name="api v1 invoices create services remove",
    ),
    path(
        "api/v1/invoices/create/set_destination/to",
        v1.invoices.create.set_destination.set_destination_to,
        name="api v1 invoices create set_destination to",
    ),
    path(
        "api/v1/invoices/create/set_destination/from",
        v1.invoices.create.set_destination.set_destination_from,
        name="api v1 invoices create set_destination from",
    ),
    path("login/", other.login.login_page, name="login"),
    path("logout/", other.login.logout_view, name="logout"),
    # path('logout_test/', other.login.logout_view, name='logout_test'),
    path(
        "login/create_account",
        other.login.create_account_page,
        name="login create_account",
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
    # path('api/v1/user/profile/toggle_theme', api.v1.user.profile.toggle_theme, name='api v1 user toggle_theme'),
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
