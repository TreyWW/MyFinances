import random

from django.urls import reverse, resolve
from model_bakery import baker

from backend.finance.models import Invoice
from tests.handler import ViewTestCase, assert_url_matches_view


class InvoicesAPIFetch(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/invoices/single/fetch/"
        self.url_name = "api:finance:invoices:single:fetch"
        self.view_function_path = "backend.finance.api.invoices.fetch.fetch_all_invoices"

    def test_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page
        response = self.make_request(with_htmx=False)
        self.assertRedirects(response, f"/auth/login/?next={self.url_path}", 302)

        # Ensure that authenticated users with HTMX headers are redirected to the invoices dashboard
        self.login_user()
        response = self.make_request(with_htmx=False)
        self.assertRedirects(response, "/dashboard/invoices/single/", 302)

    def test_302_for_non_authenticated_users(self):
        # Ensure that non-authenticated users receive a 302 status code
        response = self.make_request(with_htmx=True)
        self.assertEqual(response.status_code, 302)

    def test_200_for_authenticated_users_with_htmx(self):
        # Ensure that authenticated users with HTMX headers receive a 200 status code
        self.login_user()
        response = self.make_request()
        self.assertEqual(response.status_code, 200)

    def test_404_for_authenticated_users_no_htmx(self):
        # Ensure that authenticated users without HTMX headers are redirected to the invoices dashboard
        self.login_user()
        response = self.make_request(with_htmx=False)
        self.assertRedirects(response, "/dashboard/invoices/single/", 302)

    def test_matches_with_urls_view(self):
        assert_url_matches_view(
            self.url_path,
            self.url_name,
            self.view_function_path,
        )

    def test_no_invoices_get_returned_on_first(self):
        # Ensure that no invoices are returned when the user has no invoices
        self.login_user()
        response = self.make_request()
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

        response = self.make_request()
        self.assertEqual(response.status_code, 200)

        # Check that the number of invoices returned matches the number created
        self.assertEqual(len(response.context.get("invoices")), random_amount_of_invoices)

        # Check that all created invoices are in the response
        for invoice in invoices:
            self.assertIn(invoice, response.context.get("invoices"))


class InvoicesAPIDelete(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/invoices/single/delete/"
        self.url_name = "api:finance:invoices:single:delete"
        self.view_function_path = "backend.finance.api.invoices.delete.delete_invoice"

    def test_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page
        response = self.make_request(with_htmx=False)
        self.assertRedirects(response, f"/auth/login/?next={self.url_path}", 302)

        # Ensure that authenticated users with HTMX headers are redirected to the invoices dashboard
        self.login_user()
        response = self.make_request(with_htmx=False)
        self.assertEqual(response.status_code, 405)

    def test_matches_with_urls_view(self):
        assert_url_matches_view(
            self.url_path,
            self.url_name,
            self.view_function_path,
        )

    # def test_delete_works(self):
    #     self.login_user()
    #     invoices = baker.make("backend.Invoice", _quantity=1, user=self.log_in_user)
    #     response = self.make_request(
    #         method="delete", data={"invoice": 1}, format="json"
    #     )
    #     self.assertEqual(response.status_code, 200)

    #
    # response_content = json.loads(response.content.decode("utf-8"))
    # self.assertEqual(response_content.get("message"), "Invoice not found")


class InvoicesEditDiscount(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/invoices/single/edit/discount/"
        self.url_name = "api:finance:invoices:single:edit discount"
        self.view_function_path = "backend.finance.api.invoices.edit.edit_discount"
        self.invoice: Invoice = baker.make("backend.Invoice", user=self.log_in_user)

    def test_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page

        response = self.client.post(reverse(self.url_name, kwargs={"invoice_id": self.invoice.id}))
        self.assertRedirects(response, f"/auth/login/?next=/api/invoices/single/edit/{self.invoice.id}/discount/", 302)

        # Ensure that authenticated users with HTMX headers are redirected to the invoices dashboard
        self.login_user()
        response = self.client.post(reverse(self.url_name, kwargs={"invoice_id": self.invoice.id}))
        self.assertRedirects(response, "/dashboard/invoices/single/", 302)

    def test_valid_edit_percentage(self):
        self.login_user()
        amount = 20

        response = self.client.post(
            reverse(self.url_name, kwargs={"invoice_id": self.invoice.id}),
            {"discount_type": "on", "percentage_amount": amount},
            **self.htmx_headers,
        )

        self.assertTrue(response.status_code, 200)

        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Discount was applied successfully")
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.discount_percentage, amount)

    def test_invalid_edit_percentages(self):
        self.login_user()
        amounts = [-1, -100, "", 101, 10000]

        for amount in amounts:
            response = self.client.post(
                reverse(self.url_name, kwargs={"invoice_id": self.invoice.id}),
                {"discount_type": "on", "percentage_amount": amount},
                **self.htmx_headers,
            )

            self.assertTrue(response.status_code, 400)

            messages = self.get_all_messages(response)
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), "Please enter a valid percentage amount (between 0 and 100)")

    def test_valid_edit_amount(self):
        self.login_user()
        amount = 20

        response = self.client.post(
            reverse(self.url_name, kwargs={"invoice_id": self.invoice.id}),
            {"discount_type": "off", "discount_amount": amount},
            **self.htmx_headers,
        )

        self.assertTrue(response.status_code, 200)

        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Discount was applied successfully")
        self.invoice.refresh_from_db()
        self.assertEqual(self.invoice.discount_amount, amount)

    def test_invalid_edit_amounts(self):
        self.login_user()
        amounts = [-1, -100, "", "abc"]

        for amount in amounts:
            response = self.client.post(
                reverse(self.url_name, kwargs={"invoice_id": self.invoice.id}),
                {"discount_type": "off", "discount_amount": amount},
                **self.htmx_headers,
            )

            self.assertTrue(response.status_code, 400)

            messages = self.get_all_messages(response)
            self.assertEqual(len(messages), 1)
            self.assertEqual(str(messages[0]), "Please enter a valid discount amount")
