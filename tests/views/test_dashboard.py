from django.urls import reverse, resolve
from tests.handler import ViewTestCase


class DashboardViewTestCase(ViewTestCase):
    def test_dashboard_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_view_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_matches_with_urls_view(self):
        func = resolve("/dashboard/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/", reverse("dashboard"))
        self.assertEqual("backend.core.views.other.index.dashboard", func_name)
