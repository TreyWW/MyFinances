from django.urls import reverse, resolve

from backend.core.views.auth.login import logout_view
from tests.handler import ViewTestCase


class OtherItemsTestCase(ViewTestCase):
    def test_logout_from_url_not_logged_in_redirects(self):
        response = self.client.get(reverse("auth:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(resolve(reverse("auth:logout")).func, logout_view)

    def test_logout_from_url_logged_in(self):
        self.login_user()
        response = self.client.get(reverse("auth:logout"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("auth:login"))

    def testlogin_view_matches_with_urls_view(self):
        # func = resolve("/login/").func
        # func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual(
            "/auth/login/",
            reverse("auth:login"),
        )
