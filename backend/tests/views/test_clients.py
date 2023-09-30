from django.urls import reverse, resolve
from .handler import ViewTestCase


class InvoicesViewTestCase(ViewTestCase):
    def test_clients_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("clients dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_clients_view_200_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("clients dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_clients_view_matches_with_template(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("clients dashboard"))
        self.assertTemplateUsed(response, "core/pages/clients/dashboard/dashboard.html")

    def test_clients_view_matches_with_urls_view(self):
        func = resolve("/dashboard/clients/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/clients/", reverse("clients dashboard"))
        self.assertEqual(
            "backend.views.core.clients.dashboard.clients_dashboard", func_name
        )
