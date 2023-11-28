import random

from django.urls import reverse, resolve

from backend.models import Client
from tests.handler import ViewTestCase
from model_bakery import baker


class InvoicesAPIFetch(ViewTestCase):
    def test_302_for_all_normal_get_requests(self):
        # All should be redirected as it should only accept from HTMX
        response = self.client.get(reverse("api:invoices:fetch"))
        self.assertRedirects(response, "/login/?next=/api/invoices/fetch", 302)
        self.login_user()
        response = self.client.get(reverse("api:invoices:fetch"))
        self.assertRedirects(response, "/dashboard/invoices/", 302)

    def test_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("api:invoices:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 302)

    def test_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(reverse("api:invoices:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

    def test_matches_with_urls_view(self):
        func = resolve("/api/invoices/fetch").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/api/invoices/fetch", reverse("api:invoices:fetch"))
        self.assertEqual("backend.api.invoices.fetch.fetch_all_invoices", func_name)

    def test_no_clients_get_returned_on_first(self):
        self.login_user()
        response = self.client.get(reverse("api:invoices:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("invoices")), 0)

    def test_clients_get_returned(self):
        self.login_user()

        random_amount_of_clients = random.randrange(2, 10)
        # Use baker to create random amount of  clients
        clients = baker.make(
            "backend.Invoice", _quantity=random_amount_of_clients, user=self.log_in_user
        )

        response = self.client.get(reverse("api:invoices:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

        # Check that the number of clients returned matches the number created
        self.assertEqual(
            len(response.context.get("invoices")), random_amount_of_clients
        )

        # Check that all created clients are in the response
        for client in clients:
            self.assertIn(client, response.context.get("invoices"))
