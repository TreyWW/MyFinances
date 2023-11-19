from django.urls import reverse, resolve

from backend.models import LoginLog, AuditLog
from .handler import ViewTestCase

from backend.views.core.other.login import logout_view


class OtherItemsTestCase(ViewTestCase):
    def test_logout_from_url_not_logged_in_redirects(self):
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(resolve(reverse("logout")).func, logout_view)
        self.assertEqual(response.url, reverse("login"))

    def test_logout_from_url_logged_in(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

    def testlogin_view_matches_with_urls_view(self):
        # func = resolve("/login/").func
        # func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual(
            "/login/",
            reverse("login"),
        )

    #         self.assertEqual("backend.views.core.other.login.login_page", func_name)

    def test_login_redirects_on_already_logged_in(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_login_get_page_loads(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/login.html")

    def test_login_actually_logs_you_in(self):
        response = self.client.post(
            reverse("login"), {"email": "user", "password": "user"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))
        self.assertEqual(self.client.session["_auth_user_id"], "1")

        login_log = LoginLog.objects.first()
        audit_log = AuditLog.objects.first()
        self.assertIsNotNone(login_log)
        self.assertIsNotNone(audit_log)
        self.assertEqual(login_log.user, response.wsgi_request.user)
        self.assertEqual(audit_log.user, response.wsgi_request.user)
        self.assertEqual(audit_log.action, "Login")

    def test_login_fails_on_invalid_pass(self):
        response = self.client.post(
            reverse("login"), {"email": "user", "password": "invalid"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/login.html")
        self.assertEqual(response.context["attempted_email"], "user")
