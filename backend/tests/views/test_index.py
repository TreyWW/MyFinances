from django.urls import reverse
from .handler import ViewTestCase


class IndexViewTestCase(ViewTestCase):
    def test_index_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_index_view_302_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
