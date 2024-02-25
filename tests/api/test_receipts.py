import random

from django.urls import reverse
from model_bakery import baker

from tests.handler import ViewTestCase, assert_url_matches_view


class ReceiptsAPIFetch(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/receipts/fetch/"
        self.url_name = "api:receipts:fetch"
        self.view_function_path = "backend.api.receipts.fetch.fetch_all_receipts"

    def test_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, f"/auth/login/?next={self.url_path}", 302)

        # Ensure that authenticated users are redirected to the receipts dashboard
        self.login_user()
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, "/dashboard/receipts/", 302)

    def test_302_for_non_authenticated_users(self):
        # Ensure that non-authenticated users receive a 302 status code
        response = self.make_request()
        self.assertEqual(response.status_code, 302)

    def test_200_for_authenticated_users(self):
        # Ensure that authenticated users receive a 200 status code with HTMX headers
        self.login_user()
        response = self.make_request()
        self.assertEqual(response.status_code, 200)

    def test_matches_with_urls_view(self):
        assert_url_matches_view(self.url_path, self.url_name, self.view_function_path)

    def test_no_receipts_get_returned_on_first(self):
        # Ensure that no receipts are returned when user has no receipts
        self.login_user()
        response = self.make_request()
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

        response = self.make_request()
        self.assertEqual(response.status_code, 200)

        # Check that the number of clients returned matches the number created
        self.assertEqual(len(response.context.get("receipts")), random_amount_of_clients)

        # Check that all created clients are in the response
        for receipt in receipts:
            self.assertIn(receipt, response.context.get("receipts"))
