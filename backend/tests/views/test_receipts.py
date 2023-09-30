from django.urls import reverse, resolve
from .handler import ViewTestCase


class ReceiptsViewTestCase(ViewTestCase):
    def test_receipts_dashboard_view_302_for_non_authenticated_users(self):
        response = self.client.get(reverse("receipts dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_receipts_dashboard_view_200_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(reverse("receipts dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_receipts_dashboard_view_matches_with_urls_view(self):
        func = resolve("/dashboard/receipts").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/receipts", reverse("receipts dashboard"))
        self.assertEqual(
            "backend.views.core.receipts.dashboard.receipts_dashboard", func_name
        )
