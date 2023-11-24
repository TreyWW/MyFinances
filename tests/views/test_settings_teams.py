from django.urls import reverse, resolve

from tests.handler import ViewTestCase


class UserSettingsTeamsDashboardViewTestCase(ViewTestCase):
    def test_teams_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("user settings teams"))
        self.assertEqual(response.status_code, 302)

    def test_teams_view_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(reverse("user settings teams"))
        self.assertEqual(response.status_code, 200)

    def test_teams_view_matches_with_urls_view(self):
        path = "/dashboard/settings/teams"
        func = resolve(path).func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("backend.views.core.settings.teams.teams_dashboard", func_name)
        self.assertEqual(path, reverse("user settings teams"))
