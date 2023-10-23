from django.urls import reverse, resolve
from .handler import ViewTestCase

from model_bakery import baker


class ReceiptsViewTestCase(ViewTestCase):
    def setUp(self):
        super().setUp()

        self._receipts_dashboard_url = reverse("receipts dashboard")

    def test_receipts_dashboard_view_302_for_non_authenticated_users(self):
        response = self.client.get(self._receipts_dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_receipts_dashboard_view_200_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(self._receipts_dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_receipts_dashboard_view_matches_with_urls_view(self):
        func = resolve("/dashboard/receipts").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/receipts", self._receipts_dashboard_url)
        self.assertEqual(
            "backend.views.core.receipts.dashboard.receipts_dashboard", func_name
        )

    def test_receipts_dashboard_view_search_text(self):
        _quantity = 1
        search_text = "text"

        baker.make(
            "backend.Receipt",
            user=self.log_in_user,
            name=search_text,
            _quantity=_quantity,
        )

        data = {"search": search_text}
        self.client.login(username="user", password="user")
        response = self.client.post(self._receipts_dashboard_url, data)
        self.assertEqual(len(response.context["receipts"]), 1)
