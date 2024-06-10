from django.urls import reverse, resolve

from backend.models import Client
from tests.handler import ViewTestCase
from model_bakery import baker


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

    def test_search_functionality(self):
        # Log in the user
        self.login_user()

        # Create some clients with different names, emails, and IDs
        client_attributes = [
            {"name": "Client1", "email": "client1@example.com", "id": 1},
            {"name": "Client2", "email": "client2@example.com", "id": 2},
            {"name": "Client3", "email": "client3@example.com", "id": 3},
            {"name": "Client4", "email": "client4@example.com", "id": 4},
            {"name": "Client5", "email": "client5@example.com", "id": 5},
            {"name": "Special_Client", "email": "special@example.com", "id": 6},
        ]
        clients = [baker.make("backend.Client", user=self.log_in_user, **attrs) for attrs in client_attributes]

        # Define the URL with the search query parameter
        url = reverse("api:clients:fetch")
        headers = {"HTTP_HX-Request": "true"}

        # Define search queries to cover various edge cases
        search_queries = [
            # Exact matches
            {"query": "Client1", "expected_clients": [clients[0]]},
            {"query": "client2@example.com", "expected_clients": [clients[1]]},
            {"query": "3", "expected_clients": [clients[2]]},
            # Substring matches
            {"query": "Client", "expected_clients": clients},
            {"query": "example.com", "expected_clients": clients},
            # Case insensitivity
            {"query": "client3@example.com", "expected_clients": [clients[2]]},
            {"query": "CLIENT4", "expected_clients": [clients[3]]},
            {"query": "ClieNT1", "expected_clients": [clients[0]]},
            # Empty query
            {"query": "", "expected_clients": clients},
            # Nonexistent query
            {"query": "NonExistentClient", "expected_clients": []},
            {"query": "client8@example.com", "expected_clients": []},
        ]

        for search in search_queries:
            response = self.client.get(url, {"search": search["query"]}, **headers)
            self.assertEqual(response.status_code, 200)

            # Verify that the "clients" context variable is set
            returned_clients = response.context.get("clients")
            self.assertIsNotNone(returned_clients, f"Context variable 'clients' should not be None for query: {search['query']}")

            # Convert QuerySet to list for easy comparison
            returned_clients_list = list(returned_clients)

            # Verify that the returned clients match the expected clients
            expected_clients = search["expected_clients"]
            self.assertEqual(
                len(returned_clients_list), len(expected_clients), f"Mismatch in number of clients for query: {search['query']}"
            )
            for client in expected_clients:
                self.assertIn(client, returned_clients_list, f"Client {client} should be in the response for query: {search['query']}")
