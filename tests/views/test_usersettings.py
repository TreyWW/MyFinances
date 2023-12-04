from django.urls import reverse, resolve

from backend.models import UserSettings
from tests.handler import ViewTestCase
from django.contrib.messages import get_messages


class UserSettingsViewTestCase(ViewTestCase):
    def test_usersettings_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("user settings"))
        self.assertEqual(response.status_code, 302)

    def test_usersettings_view_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(reverse("user settings"))
        self.assertEqual(response.status_code, 200)

    def test_usersettings_view_matches_with_urls_view(self):
        func = resolve("/dashboard/settings/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/settings/", reverse("user settings"))
        self.assertEqual("backend.views.core.settings.view.settings_page", func_name)
