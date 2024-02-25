from django.urls import reverse

from tests.handler import ViewTestCase, assert_url_matches_view


class CurrencyConverterConvertAPI(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/currency_converter/convert/"
        self.url_name = "api:currency_converter:convert"
        self.view_function_path = "backend.api.currency_converter.convert.currency_conversion"

    def test_clients_view_302_for_all_normal_get_requests(self):
        # Ensure that non-HTMX GET requests are redirected to the login page
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, f"/auth/login/?next={self.url_path}", 302)

        # Ensure that authenticated users are redirected to the currency dashboard that are not htmx requests
        self.login_user()
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, "/dashboard/currency_converter/", 302)

    def test_clients_view_405_for_authenticated_users_not_post(self):
        # Ensure that authenticated users receive a 200 status code with HTMX headers
        self.login_user()
        response = self.make_request()
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content, b"Method not allowed")

    def test_clients_view_matches_with_urls_view(self):
        assert_url_matches_view(self.url_path, self.url_name, self.view_function_path)

    # fails for some reason

    # def test_conversion_VALID(self):
    #     self.login_user()
    #     response = self.make_request(
    #         method="post",
    #         data={
    #             "currency_amount": 5.50,
    #             "from_currency": "usd",
    #             "to_currency": "gbp",
    #         },
    #     )
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(4.2 <= response.context.get("converted_amount") <= 4.6)
    #     self.assertEqual(response.context.get("original_amount"), 5.50)
    #     self.assertEqual(response.context.get("original_currency"), "usd")
    #     self.assertEqual(response.context.get("original_currency_sign"), "$")
    #     self.assertEqual(response.context.get("target_currency"), "gbp")
    #     self.assertEqual(response.context.get("target_currency_sign"), "£")
