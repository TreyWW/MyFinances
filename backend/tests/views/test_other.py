from django.urls import reverse, resolve
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
