from django.urls import reverse, resolve
from backend.models import UserSettings
from tests.handler import ViewTestCase, assert_url_matches_view


class CurrencyAPIChange(ViewTestCase):
    # Setting up common data for tests
    def setUp(self):
        super().setUp()
        self.url_path = "/api/settings/change_currency/"
        self.url_name = "api:settings:change_currency"
        self.view_function_path = "backend.api.settings.currency.update_currency_view"

    # Test that the URL resolves to the correct view function
    def test_url_matches_api(self):
        assert_url_matches_view(self.url_path, self.url_name, self.view_function_path)

    # Test that the view returns a 405 Method Not Allowed for GET requests
    def test_405_for_get_requests(self):
        self.login_user()
        response = self.make_request(method="get", with_htmx=False)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode("utf-8"), "")

    # Test that the view returns a 400 Bad Request for POST requests without HTMX
    def test_400_for_all_normal_get_requests(self):
        self.login_user()
        response = self.make_request(method="post", with_htmx=False)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "Invalid Request")

    # Test that non-authenticated users are redirected to the login page for GET requests
    def test_302_for_non_authenticated_users(self):
        response = self.client.get(reverse(self.url_name))
        self.assertRedirects(response, f"/login/?next={self.url_path}", 302)

    # Test that an error message is displayed when no currency is provided in the POST request
    def test_no_currency_provided(self):
        self.login_user()
        response = self.make_request(method="post", with_htmx=True)
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Invalid Currency")

    # Test that users receive a message when trying to update to their current currency
    def test_currency_is_already_that(self):
        self.login_user()
        response = self.make_request(
            method="post", data={"currency": "GBP"}, with_htmx=True
        )
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), "You are already using this currency, no change was made"
        )

    # Test that the user's currency is updated successfully
    def test_currency_is_updated(self):
        self.login_user()
        response = self.make_request(
            method="post", data={"currency": "EUR"}, with_htmx=True
        )
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully updated currency")
        user_settings = UserSettings.objects.get(user=self.log_in_user)
        self.assertEqual(user_settings.currency, "EUR")
