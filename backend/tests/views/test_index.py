from django.urls import reverse, resolve
from .handler import ViewTestCase


class IndexViewTestCase(ViewTestCase):
    def test_index_view_200_for_non_authenticated_users(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_200_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_clients_view_matches_with_urls_view(self):
        func = resolve("/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/", reverse("index"))
        self.assertEqual("backend.views.core.other.index.index", func_name)
