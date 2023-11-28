import random
from django.urls import reverse, resolve
from backend.models import Invoice
from tests.handler import ViewTestCase
from model_bakery import baker
from tests.handler import assert_url_matches_view


class InvoicesAPIFetch(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/invoices/fetch/"
        self.url_name = "api:invoices:fetch"
        self.view_function_path = "backend.api.invoices.fetch.fetch_all_invoices"

    def test_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page
        response = self.client.get(reverse("api:invoices:fetch"))
        self.assertRedirects(response, f"/login/?next={self.url_path}", 302)

        # Ensure that authenticated users with HTMX headers are redirected to the invoices dashboard
        self.login_user()
        response = self.client.get(reverse("api:invoices:fetch"))
        self.assertRedirects(response, "/dashboard/invoices/", 302)

    def test_302_for_non_authenticated_users(self):
        # Ensure that non-authenticated users receive a 302 status code
        response = self.client.get(reverse(self.url_name), **self.htmx_headers)
        self.assertEqual(response.status_code, 302)

    def test_200_for_authenticated_users_with_htmx(self):
        # Ensure that authenticated users with HTMX headers receive a 200 status code
        self.login_user()
        response = self.client.get(reverse(self.url_name), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

    def test_404_for_authenticated_users_no_htmx(self):
        # Ensure that authenticated users without HTMX headers are redirected to the invoices dashboard
        self.login_user()
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, "/dashboard/invoices/", 302)

    def test_matches_with_urls_view(self):
        assert_url_matches_view(
            self.url_path,
            self.url_name,
            self.view_function_path,
        )

    def test_no_invoices_get_returned_on_first(self):
        # Ensure that no invoices are returned when user has no invoices
        self.login_user()
        response = self.client.get(reverse(self.url_name), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context.get("invoices")), 0)

    def test_invoices_get_returned(self):
        # Ensure that the correct number of invoices are returned for authenticated users
        self.login_user()

        random_amount_of_invoices = random.randrange(2, 10)
        # Use baker to create a random amount of invoices
        invoices = baker.make(
            "backend.Invoice",
            _quantity=random_amount_of_invoices,
            user=self.log_in_user,
        )

        response = self.client.get(reverse(self.url_name), **self.htmx_headers)
        self.assertEqual(response.status_code, 200)

        # Check that the number of invoices returned matches the number created
        self.assertEqual(
            len(response.context.get("invoices")), random_amount_of_invoices
        )

        # Check that all created invoices are in the response
        for invoice in invoices:
            self.assertIn(invoice, response.context.get("invoices"))
