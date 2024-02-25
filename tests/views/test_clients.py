from django.urls import reverse, resolve

from backend.models import Client
from tests.handler import ViewTestCase


class ClientsViewTestCase(ViewTestCase):
    def test_clients_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("clients dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_clients_view_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(reverse("clients dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_clients_view_matches_with_template(self):
        self.login_user()
        response = self.client.get(reverse("clients dashboard"))
        self.assertTemplateUsed(response, "pages/clients/dashboard/dashboard.html")

    def test_clients_view_matches_with_urls_view(self):
        func = resolve("/dashboard/clients/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/clients/", reverse("clients dashboard"))
        self.assertEqual("backend.views.core.clients.dashboard.clients_dashboard", func_name)

    def test_clients_view_doesnt_create_invalid_client_no_first_name(self):
        self.login_user()
        client_objects_before = Client.objects.count()
        response = self.client.post(
            reverse("clients dashboard"),
            {
                "first_name": "",
                "last_name": "Testy",
            },
        )
        client_objects_after = Client.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_objects_after, client_objects_before)

    def test_clients_view_doesnt_create_invalid_client_no_last_name(self):
        self.login_user()
        client_objects_before = Client.objects.count()
        response = self.client.post(
            reverse("clients dashboard"),
            {
                "first_name": "Testy",
                "last_name": "",
            },
        )
        client_objects_after = Client.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(client_objects_after, client_objects_before)
