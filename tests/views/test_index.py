from django.urls import reverse, resolve
from tests.handler import ViewTestCase


class IndexViewTestCase(ViewTestCase):
    def test_index_view_200_for_non_authenticated_users(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_200_for_authenticated_users(self):
        self.login_user()
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_clients_view_matches_with_urls_view(self):
        func = resolve("/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/", reverse("index"))
        self.assertEqual("backend.core.views.other.index.index", func_name)
