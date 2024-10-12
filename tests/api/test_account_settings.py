from django.urls import reverse

from backend.models import UserSettings, User
from tests.handler import ViewTestCase, assert_url_matches_view


class CurrencyAPIChange(ViewTestCase):
    # Setting up common data for tests
    def setUp(self):
        super().setUp()
        self.url_path = "/api/settings/account_preferences/"
        self.url_name = "api:settings:account_preferences"
        self.view_function_path = "backend.core.api.settings.preferences.update_account_preferences"

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
        self.assertRedirects(response, f"/auth/login/?next={self.url_path}", 302)

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
        response = self.make_request(method="post", data={"currency": "GBP"}, with_htmx=True)
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully updated preferences")

    # Test that the user's currency is updated successfully
    def test_currency_is_updated(self):
        self.login_user()
        response = self.make_request(method="post", data={"currency": "EUR"}, with_htmx=True)
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully updated preferences")
        user_settings = UserSettings.objects.get(user=self.log_in_user)
        self.assertEqual(user_settings.currency, "EUR")


class AccountNameChange(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.url_path = "/api/settings/change_name/"
        self.url_name = "api:settings:change_name"
        self.view_function_path = "settings.change_name.change_name"

    def test_405_for_non_htmx_requests(self):
        # Ensure that non-HTMX requests to the endpoint result in a 405 Method Not Allowed response
        self.login_user()
        response = self.make_request(method="post", with_htmx=False)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(response.content.decode(), "Invalid Request")

    def test_redirects_to_login_for_unauthenticated_users(self):
        # Ensure that unauthenticated users are redirected to the login page
        response = self.make_request()
        self.assertRedirects(response, f"/auth/login/?next={self.url_path}", 302)

    def test_validation_error_no_name_provided(self):
        # Ensure that a validation error message is displayed when neither a first name nor a last name is provided
        self.login_user()
        response = self.make_request(method="post", with_htmx=True)
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Please enter a valid firstname or lastname.")

    def test_name_didnt_change(self):
        # Ensure that a warning message is displayed when the provided name is the same as the current name
        self.login_user()
        self.log_in_user.first_name = "John"
        self.log_in_user.last_name = "Doe"
        self.log_in_user.save()
        response = self.make_request(
            method="post",
            data={"first_name": "John", "last_name": "Doe"},
            with_htmx=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You already have this name.")

    def test_name_changed_successfully(self):
        # Ensure that the name is successfully changed, and a success message is displayed
        self.login_user()
        response = self.make_request(
            method="post",
            data={"first_name": "New", "last_name": "Name"},
            with_htmx=True,
        )
        self.assertEqual(response.status_code, 200)
        messages = self.get_all_messages(response)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "Successfully changed your name to <strong>New Name</strong>",
        )
        # get updated user obj
        user = User.objects.get(id=self.log_in_user.id)
        self.assertEqual("New Name", user.get_full_name())
