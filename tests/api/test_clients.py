import random

from django.urls import reverse
from model_bakery import baker

from tests.handler import ViewTestCase, assert_url_matches_view


class ClientsAPIFetch(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/clients/fetch/"
        self.url_name = "api:clients:fetch"
        self.view_function_path = "backend.api.clients.fetch.fetch_all_clients"

    def test_clients_view_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, f"/auth/login/?next={self.url_path}", 302)

        # Ensure that authenticated users are redirected to the clients dashboard
        self.login_user()
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, "/dashboard/clients/", 302)

    def test_clients_view_302_for_non_authenticated_users(self):
        # Ensure that non-authenticated users receive a 302 status code
        response = self.make_request()
        self.assertEqual(response.status_code, 302)

    def test_clients_view_200_for_authenticated_users(self):
        # Ensure that authenticated users receive a 200 status code with HTMX headers
        self.login_user()
        response = self.make_request()
        self.assertEqual(response.status_code, 200)

    def test_clients_view_matches_with_urls_view(self):
        assert_url_matches_view(self.url_path, self.url_name, self.view_function_path)

    def test_no_clients_get_returned_on_first(self):
        # Ensure that no clients are returned when user has no clients
        self.login_user()
        response = self.make_request()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("clients")), 0)

    def test_clients_get_returned(self):
        # Ensure that the correct number of clients are returned for authenticated users
        self.login_user()

        random_amount_of_clients = random.randrange(2, 10)
        # Use baker to create a random amount of clients
        clients = baker.make("backend.Client", _quantity=random_amount_of_clients, user=self.log_in_user)

        response = self.make_request()
        self.assertEqual(response.status_code, 200)

        # Check that the number of clients returned matches the number created
        self.assertEqual(len(response.context.get("clients")), random_amount_of_clients)

        # Check that all created clients are in the response
        for client in clients:
            self.assertIn(client, response.context.get("clients"))

    def test_search_functionality(self):
        # Log in the user
        self.login_user()

        # Create some clients with different names, emails, and IDs
        client1 = baker.make("backend.Client", name="John Doe", email="john@example.com", id=1, user=self.log_in_user)
        client2 = baker.make("backend.Client", name="Trey", email="trey@example.com", id=2, user=self.log_in_user)
        client3 = baker.make("backend.Client", name="Jacob Johnson", email="jacob@example.com", id=3, user=self.log_in_user)

        # Define the URL with the search query parameter
        url = reverse(self.url_name)
        headers = {"HTTP_HX-Request": "true"}

        # Test searching by name
        response = self.client.get(url, {"search": "John"}, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(client1, response.context["clients"])
        self.assertNotIn(client2, response.context["clients"])
        self.assertIn(client3, response.context["clients"])  # Jacob Johnson contains "John"

        # Test searching by email
        response = self.client.get(url, {"search": "trey@example.com"}, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(client2, response.context["clients"])
        self.assertNotIn(client1, response.context["clients"])
        self.assertNotIn(client3, response.context["clients"])

        # Test searching by ID
        response = self.client.get(url, {"search": "3"}, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(client3, response.context["clients"])
        self.assertNotIn(client1, response.context["clients"])
        self.assertNotIn(client2, response.context["clients"])

        # Test searching with a substring
        response = self.client.get(url, {"search": "Tr"}, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(client2, response.context["clients"])
        self.assertNotIn(client1, response.context["clients"])
        self.assertNotIn(client3, response.context["clients"])

        # Test searching with an empty query
        response = self.client.get(url, {"search": ""}, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertIn(client1, response.context["clients"])
        self.assertIn(client2, response.context["clients"])
        self.assertIn(client3, response.context["clients"])
