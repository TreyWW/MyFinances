from django.contrib.messages import get_messages
from django.urls import reverse

from backend.models import User
from tests.handler import ViewTestCase


class LoginTestCases(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/invoices/fetch/"
        self.url_name = "auth:login"
        self.view_function_path = "backend.finance.api.invoices.fetch.fetch_all_invoices"
        self.login_rev = reverse("auth:login")

    def test_login_redirects_for_auth_user(self):
        self.client.force_login(User.objects.first())  # Log in as an authenticated user
        response = self.client.get(self.login_rev)
        self.assertEqual(response.status_code, 302)

    def test_login_works_for_unauth_user(self):
        response = self.client.get(self.login_rev)
        self.assertEqual(response.status_code, 200)

    # def test_actual_login_functionality(self):
    #     response = self.client.post(
    #         self.login_rev, {"email": "user@example.com", "password": "user"}
    #     )
    #     messages = list(get_messages(response.wsgi_request))
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(response.wsgi_request.user.is_authenticated)
    #     self.assertEqual(response.wsgi_request.user.id, self.log_in_user.id)
    #     #
    #     response = self.client.get(self.login_rev)
    #     self.assertEqual(response.status_code, 302)

    # def test_actual_login_functionality_fails_on_invalid(self):
    #     response = self.client.post(
    #         self.login_rev, {"email": "user@example.com", "password": "invalid"}
    #     )
    #     messages = list(get_messages(response.wsgi_request))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFalse(response.wsgi_request.user.is_authenticated)
    #     self.assertEqual(response.wsgi_request.user.id, None)
    #     self.assertEqual(len(messages), 1)
    #     self.assertEqual(messages[0].message, "Invalid email or password")
    #     self.assertEqual(response.context.get("attempted_email"), "user@example.com")


class CreateAccount(ViewTestCase):
    def test_manual_passwords_dont_match(self):
        response = self.client.post(
            reverse("auth:login create_account manual"),
            {
                "email": "user@example.com",
                "password": "user",
                "confirm_password": "invalid",
            },
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.id, None)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Passwords don't match")

    def test_manual_invalid_email(self):
        response = self.client.post(
            reverse("auth:login create_account manual"),
            {"email": "invalid", "password": "user", "confirm_password": "user"},
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.id, None)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Invalid email")

    def test_manual_invalid_password(self):
        response = self.client.post(
            reverse("auth:login create_account manual"),
            {
                "email": "valid@example.com",
                "password": "user",  # too short (min is 6)
                "confirm_password": "user",  # too short (min is 6)
            },
        )
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertEqual(response.wsgi_request.user.id, None)
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "Password must be at least 6 characters")

    # def test_manual_email_taken(self):
    #     response = self.client.post(
    #         reverse("auth:login create_account manual"),
    #         {
    #             "email": "user@example.com",
    #             "password": "user12",
    #             "confirm_password": "user12",
    #         },
    #     )
    #     messages = list(get_messages(response.wsgi_request))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertFalse(response.wsgi_request.user.is_authenticated)
    #     self.assertEqual(response.wsgi_request.user.id, None)
    #     self.assertEqual(len(messages), 1)
    #     self.assertEqual(messages[0].message, "Email is already taken")

    # def test_manual_success(self):
    #     response = self.client.post(
    #         reverse("auth:login create_account manual"),
    #         {
    #             "email": "user2@google.com",
    #             "password": "user12",
    #             "confirm_password": "user12",
    #         },
    #     )
    #     self.assertEqual(response.status_code, 302)
    #     self.assertTrue(response.wsgi_request.user.is_authenticated)
    #     self.assertEqual(response.wsgi_request.user.id, 2)


class TestLogout(ViewTestCase):
    def test_logout_for_authenticated_user(self):
        self.client.force_login(User.objects.first())  # Log in as an authenticated user
        response = self.client.get(reverse("auth:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(response.wsgi_request.user.is_authenticated)  # check to make sure no longer authenticated
        self.assertEqual(response.wsgi_request.user.id, None)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].message, "You've now been logged out.")

    # def test_logout_fails_for_unauthenticated_user(self):
    #     response = self.client.get(reverse("auth:logout"))
    #     self.assertFalse(
    #         response.wsgi_request.user.is_authenticated
    #     )  # check to make sure no longer authenticated
    #     self.assertEqual(response.wsgi_request.user.id, None)
    #     self.assertRedirects(response, reverse("auth:login"), status_code=302)
