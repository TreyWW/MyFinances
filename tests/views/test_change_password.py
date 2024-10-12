from django.contrib.auth.hashers import check_password
from django.contrib.messages import get_messages
from django.urls import reverse, resolve

from tests.handler import ViewTestCase


class ChangePasswordViewTestCase(ViewTestCase):
    def test_change_password_view_302_for_non_authenticated_users_GET(self):
        response = self.client.get(reverse("settings:change_password"))
        self.assertEqual(response.status_code, 302)

    def test_change_password_view_200_for_authenticated_users_GET(self):
        self.login_user()
        response = self.client.get(reverse("settings:change_password"))
        self.assertEqual(response.status_code, 200)

    def test_change_password_view_302_for_non_authenticated_users_POST(self):
        response = self.client.get(reverse("settings:change_password"))
        self.assertEqual(response.status_code, 302)

    def test_change_password_view_200_for_authenticated_users_POST_valid_password(self):
        self.login_user()
        response = self.client.post(
            reverse("settings:change_password"),
            {
                "current_password": "user",
                "password": "changed_password",
                "confirm_password": "changed_password",
            },
        )

        self.assertTrue(check_password("changed_password", response.wsgi_request.user.password))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully changed your password.")

        self.assertEqual(response.status_code, 302)

    def test_change_password_view_200_for_authenticated_users_POST_invalid_no_password(
        self,
    ):
        self.login_user()
        response = self.client.post(reverse("settings:change_password"), {"current_password": "user"})

        self.assertTrue(check_password("user", response.wsgi_request.user.password))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Something went wrong, no password was provided.")

        self.assertEqual(response.status_code, 302)

    def test_change_password_view_200_for_authenticated_users_POST_invalid_current_password(
        self,
    ):
        self.login_user()
        response = self.client.post(reverse("settings:change_password"), {})

        self.assertTrue(check_password("user", response.wsgi_request.user.password))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Incorrect current password")

        self.assertEqual(response.status_code, 302)

    def test_change_password_view_200_for_authenticated_users_POST_invalid_password_too_short(
        self,
    ):
        self.login_user()
        response = self.client.post(
            reverse("settings:change_password"),
            {
                "current_password": "user",
                "password": "pass",
                "confirm_password": "pass",
            },
        )

        self.assertTrue(check_password("user", response.wsgi_request.user.password))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Password must be between 8 and 128 characters.",
        )

        self.assertEqual(response.status_code, 302)

    def test_change_password_view_200_for_authenticated_users_POST_invalid_confirm_is_different(
        self,
    ):
        self.login_user()
        response = self.client.post(
            reverse("settings:change_password"),
            {
                "current_password": "user",
                "password": "password23",
                "confirm_password": "password",
            },
        )

        self.assertTrue(check_password("user", response.wsgi_request.user.password))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Passwords don't match",
        )

        self.assertEqual(response.status_code, 302)

    def test_change_password_view_200_for_authenticated_users_POST_invalid_password_too_long(
        self,
    ):
        self.login_user()
        response = self.client.post(
            reverse("settings:change_password"),
            {
                "current_password": "user",
                "password": "p" * 129,
                "confirm_password": "p" * 129,
            },
        )

        self.assertTrue(check_password("user", response.wsgi_request.user.password))

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Password must be between 8 and 128 characters.",
        )

        self.assertEqual(response.status_code, 302)

    def test_change_password_view_matches_with_urls_view(self):
        func = resolve("/dashboard/settings/profile/change_password/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual(
            "/dashboard/settings/profile/change_password/",
            reverse("settings:change_password"),
        )
        self.assertEqual("backend.core.views.settings.view.change_password", func_name)
