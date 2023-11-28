import random
from django.urls import reverse, resolve
from backend.models import Receipt
from tests.handler import ViewTestCase
from model_bakery import baker


class ReceiptsAPIFetch(ViewTestCase):
    def test_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page
        response = self.client.get(reverse("api:receipts:fetch"))
        self.assertRedirects(response, "/login/?next=/api/receipts/fetch", 302)

        # Ensure that authenticated users are redirected to the receipts dashboard
        self.login_user()
        response = self.client.get(reverse("api:receipts:fetch"))
        self.assertRedirects(response, "/dashboard/receipts/", 302)

    def test_302_for_non_authenticated_users(self):
        # Ensure that non-authenticated users receive a 302 status code
        response = self.client.get(reverse("api:receipts:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 302)

    def test_200_for_authenticated_users(self):
        # Ensure that authenticated users receive a 200 status code with HTMX headers
        self.login_user()
        response = self.client.get(reverse("api:receipts:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

    def test_matches_with_urls_view(self):
        # Ensure that the URL reversal and view function match as expected
        func = resolve("/api/receipts/fetch").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/api/receipts/fetch", reverse("api:receipts:fetch"))
        self.assertEqual("backend.api.receipts.fetch.fetch_all_receipts", func_name)

    def test_no_receipts_get_returned_on_first(self):
        # Ensure that no receipts are returned when user has no receipts
        self.login_user()
        response = self.client.get(reverse("api:receipts:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("receipts")), 0)

    def test_clients_get_returned(self):
        # Ensure that the correct number of receipts are returned for authenticated users
        self.login_user()

        random_amount_of_clients = random.randrange(2, 10)
        # Use baker to create a random amount of clients
        receipts = baker.make(
            "backend.Receipt",
            _quantity=random_amount_of_clients,
            _create_files=True,
            user=self.log_in_user,
        )

        response = self.client.get(reverse("api:receipts:fetch"), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

        # Check that the number of clients returned matches the number created
        self.assertEqual(
            len(response.context.get("receipts")), random_amount_of_clients
        )

        # Check that all created clients are in the response
        for receipt in receipts:
            self.assertIn(receipt, response.context.get("receipts"))
