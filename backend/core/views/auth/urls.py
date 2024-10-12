from django.urls import path

from . import login, create_account, verify
from .passwords import view as passwords_view, generate as passwords_generate, set as passwords_set

urlpatterns = [
    path("login/", login.login_initial_page, name="login"),
    path("login/manual/", login.login_manual, name="login manual"),
    path("login/magic_link/request/", login.MagicLinkRequestView.as_view(), name="login magic_link request"),
    path("login/magic_link/request/wait/", login.MagicLinkWaitingView.as_view(), name="login magic_link request wait"),
    path("login/magic_link/verify/<uuid:uuid>/<str:token>/", login.MagicLinkVerifyView.as_view(), name="login magic_link verify"),
    path(
        "login/magic_link/verify/<uuid:uuid>/<str:token>/accept/",
        login.MagicLinkVerifyAccept.as_view(),
        name="login magic_link verify accept",
    ),
    path(
        "login/magic_link/verify/<uuid:uuid>/<str:token>/decline/",
        login.MagicLinkVerifyDecline.as_view(),
        name="login magic_link verify decline",
    ),
    path(
        "login/forgot_password/",
        login.forgot_password_page,
        name="login forgot_password",
    ),
    path("logout/", login.logout_view, name="logout"),
    path(
        "create_account/",
        create_account.CreateAccountChooseView.as_view(),
        name="login create_account",
    ),
    path(
        "create_account/manual/",
        create_account.CreateAccountManualView.as_view(),
        name="login create_account manual",
    ),
    path(
        "create_account/verify/<uuid:uuid>/<str:token>/",
        verify.create_account_verify,
        name="login create_account verify",
    ),
    path(
        "create_account/verify/resend/",
        verify.resend_verification_code,
        name="login create_account verify resend",
    ),
    # path(
    #     "login/magic_link/<str:uuid>/",
    #     login.magic_link,
    #     name="login magic_link",
    # )
    path(
        "reset-password/",
        passwords_generate.password_reset,
        name="user set password reset",
    ),
    path(
        "set-password/<str:secret>/",
        passwords_view.set_password,
        name="user set password",
    ),
    path(
        "set-password/<str:secret>/set/",
        passwords_set.set_password_set,
        name="user set password set",
    ),
    path(
        "admin/generate-password/",
        passwords_generate.set_password_generate,
        name="admin set password generate",
    ),
]

app_name = "auth"
