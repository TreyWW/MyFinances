from django.urls import reverse, resolve

from backend.models import UserSettings
from .handler import ViewTestCase
from django.contrib.messages import get_messages


class UserSettingsViewTestCase(ViewTestCase):
    def test_usersettings_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("user settings"))
        self.assertEqual(response.status_code, 302)

    def test_usersettings_view_200_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("user settings"))
        self.assertEqual(response.status_code, 200)

    def test_usersettings_view_matches_with_urls_view(self):
        func = resolve("/dashboard/settings/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/settings/", reverse("user settings"))
        self.assertEqual("backend.views.core.settings.view.settings_page", func_name)

    def test_usersettings_currency_post_with_valid(self):
        self.client.login(username="user", password="user")
        # check default
        response = self.client.get(reverse("user settings"))
        usr_settings = UserSettings.objects.first()
        self.assertIsNotNone(usr_settings)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["currency"], "GBP")
        # change and recheck
        response = self.client.post(reverse("user settings"), {"currency": "EUR"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["currency"], "EUR")

    def test_usersettings_currency_post_with_invalid_currency(self):
        self.client.login(username="user", password="user")
        response = self.client.post(reverse("user settings"), {"currency": "invalid"})

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 2)
        self.assertEqual(str(messages[0]), "Invalid currency")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["currency"], "GBP")
