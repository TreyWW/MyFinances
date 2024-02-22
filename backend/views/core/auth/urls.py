from django.urls import path

from . import login, create_account
from .passwords import view as passwords_view
from .passwords import generate as passwords_generate
from .passwords import set as passwords_set

urlpatterns = [
    path("login/", login.login_page, name="login"),
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
        "create_account/verify/<uuid:uuid>/",
        create_account.create_account_verify,
        name="login create_account verify",
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
