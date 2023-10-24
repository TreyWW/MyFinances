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


class ReceiptsAPITestCase(ViewTestCase):
    def setUp(self):
        super().setUp()

        self._receipts_api_fetch_url = reverse("api v1 receipts fetch")

    def test_receipts_fetch_api_view_302_for_non_authenticated_users(self):
        response = self.client.get(self._receipts_api_fetch_url)
        self.assertEqual(response.status_code, 302)

    def test_receipts_fetch_api_view_404_for_authenticated_users(self):
        self.client.login(username="user", password="user")
        response = self.client.get(self._receipts_api_fetch_url)
        self.assertEqual(response.status_code, 404)

    def test_receipts_fetch_api_view_matches_with_urls_view(self):
        func = resolve("/api/v1/receipts/fetch").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/api/v1/receipts/fetch", self._receipts_api_fetch_url)
        self.assertEqual(
            "backend.views.api.v1.receipts.fetch.fetch_receipts", func_name
        )

    def test_receipts_fetch_api_view_returns_correct_amount(self):
        _quantity = 4

        baker.make(
            "backend.Receipt",
            user=self.log_in_user,
            _quantity=_quantity,
            _create_files=True,
        )
        headers = {"HTTP_HX-Request": "true"}
        self.client.force_login(self.log_in_user)
        response = self.client.get(self._receipts_api_fetch_url, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["receipts"]), 4)

    def test_receipts_fetch_api_view_search_text(self):
        search_text = "text"

        baker.make(
            "backend.Receipt",
            user=self.log_in_user,
            name=search_text,
            _quantity=1,
            _create_files=True,
        )
        # not on search
        baker.make(
            "backend.Receipt",
            user=self.log_in_user,
            name="something_random",
            _quantity=1,
            _create_files=True,
        )

        data = {"search": search_text}
        headers = {"HTTP_HX-Request": "true"}
        self.client.login(username="user", password="user")
        response = self.client.get(self._receipts_api_fetch_url, data, **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["receipts"]), 1)
