from django.urls import reverse, resolve

from backend.models import UserSettings
from tests.handler import ViewTestCase
from django.contrib.messages import get_messages


class UserSettingsAccountPreferencesViewTestCase(ViewTestCase):
    def test_usersettings_currency_post_with_valid(self):
        self.login_user()
        # check default
        response = self.client.get(reverse("user settings"))
        usr_settings = UserSettings.objects.first()
        self.assertIsNotNone(usr_settings)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["currency"], "GBP")
        # change and recheck
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(
            reverse("user settings"),
            {"currency": "EUR", "section": "account_preferences"},
            **headers,
        )
        self.assertEqual(response.status_code, 200)
        # check that only the message "successfully updated currency" is returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully updated currency")
        # check that the users currency is updated to EUR and sent back in their new request
        self.assertEqual(response.context["currency"], "EUR")

    def test_usersettings_currency_post_with_invalid_currency(self):
        self.login_user()
        # provide htmx in request
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(
            reverse("user settings"),
            {"currency": "invalid", "section": "account_preferences"},
            **headers,
        )

        # check that only the message "invalid currency" is returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Invalid currency")
        # check that response is successful
        self.assertEqual(response.status_code, 200)
        # check that the currency is still at default, and hasn't changed
        self.assertEqual(response.context["currency"], "GBP")
