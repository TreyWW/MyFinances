from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse, resolve

from backend.models import Receipt
from tests.handler import ViewTestCase
from model_bakery import baker


class ReceiptsViewTestCase(ViewTestCase):
    def setUp(self):
        super().setUp()

        # Define URLs for the receipts dashboard
        self._receipts_dashboard_url = reverse("receipts dashboard")

    def test_receipts_dashboard_view_302_for_non_authenticated_users(self):
        # Test that non-authenticated users are redirected
        response = self.client.get(self._receipts_dashboard_url)
        self.assertEqual(response.status_code, 302)

    def test_receipts_dashboard_view_200_for_authenticated_users(self):
        # Test that authenticated users get a successful response
        self.login_user()
        response = self.client.get(self._receipts_dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_receipts_dashboard_view_matches_with_urls_view(self):
        # Test that the URL resolves to the correct view function
        func = resolve("/dashboard/receipts/").func
        func_name = f"{func.__module__}.{func.__name__}"
        self.assertEqual("/dashboard/receipts/", self._receipts_dashboard_url)
        self.assertEqual("backend.finance.views.receipts.dashboard.receipts_dashboard", func_name)

    def test_search_functionality(self):
        self.login_user()

        # Create some receipts with different names, dates, merchant stores, purchase categories, and IDs
        receipt_attributes = [
            {"name": "Groceries", "date": "2024-02-01", "merchant_store": "Walmart", "purchase_category": "Food", "id": 1},
            {"name": "Electronics", "date": "2023-08-02", "merchant_store": "Best Buy", "purchase_category": "Gadgets", "id": 2},
            {"name": "Clothing", "date": "2021-01-05", "merchant_store": "Gap", "purchase_category": "Apparel", "id": 3},
            {"name": "Groceries Deluxe", "date": "2020-09-04", "merchant_store": "Whole Foods", "purchase_category": "Food", "id": 4},
            {"name": "Gadgets Plus", "date": "2022-12-05", "merchant_store": "Apple Store", "purchase_category": "Gadgets", "id": 5},
            {"name": "Special Groceries", "date": "2023-07-07", "merchant_store": "Trader Joe's", "purchase_category": "Food", "id": 6},
        ]
        receipts = [baker.make("backend.Receipt", user=self.log_in_user, **attrs) for attrs in receipt_attributes]

        # Define the URL with the search query parameter
        url = reverse("api:finance:receipts:fetch")
        headers = {"HTTP_HX-Request": "true"}

        # Define search queries to cover various edge cases
        search_queries = [
            # Exact matches
            {"query": "Groceries", "expected_receipts": [receipts[0], receipts[3], receipts[5]]},
            {"query": "2022-12-05", "expected_receipts": [receipts[4]]},
            {"query": "Best Buy", "expected_receipts": [receipts[1]]},
            {"query": "Apparel", "expected_receipts": [receipts[2]]},
            {"query": "6", "expected_receipts": [receipts[5]]},
            # Substring matches
            {"query": "Electroni", "expected_receipts": [receipts[1]]},
            {"query": "Who", "expected_receipts": [receipts[3]]},
            {"query": "Gadge", "expected_receipts": [receipts[1], receipts[4]]},
            {"query": "Foo", "expected_receipts": [receipts[0], receipts[3], receipts[5]]},
            {"query": "2023", "expected_receipts": [receipts[1], receipts[5]]},
            # Case insensitivity
            {"query": "gadgets plus", "expected_receipts": [receipts[4]]},
            {"query": "CLOTHING", "expected_receipts": [receipts[2]]},
            {"query": "groCEries deLuXe", "expected_receipts": [receipts[3]]},
            {"query": "WaLmArT", "expected_receipts": [receipts[0]]},
            {"query": "TradeR Joe'S", "expected_receipts": [receipts[5]]},
            # Empty query
            {"query": "", "expected_receipts": receipts},
            # Nonexistent query
            {"query": "NonExistentReceiptName", "expected_receipts": []},
            {"query": "Walmartt", "expected_receipts": []},
            {"query": "nonexistentstore", "expected_receipts": []},
            {"query": "10", "expected_receipts": []},
        ]

        for search in search_queries:
            response = self.client.get(url, {"search": search["query"]}, **headers)
            self.assertEqual(response.status_code, 200)

            # Verify that the "receipts" context variable is set
            returned_receipts = response.context.get("receipts")
            self.assertIsNotNone(returned_receipts, f"Context variable 'receipts' should not be None for query: {search['query']}")

            # Convert QuerySet to list for easy comparison
            returned_receipts_list = list(returned_receipts)

            # Verify that the returned receipts match the expected receipts
            expected_receipts = search["expected_receipts"]
            self.assertEqual(
                len(returned_receipts_list), len(expected_receipts), f"Mismatch in number of receipts for query: {search['query']}"
            )
            for receipt in expected_receipts:
                self.assertIn(receipt, returned_receipts_list, f"Receipt {receipt} should be in the response for query: {search['query']}")


class ReceiptsAPITestCase(ViewTestCase):
    def setUp(self):
        super().setUp()

        # Define URLs for the receipts API
        self._receipts_api_create_url = reverse("api:finance:receipts:new")

    def test_receipt_create_post_with_valid(self):
        # Test creating a receipt with valid data
        self.login_user()
        self.assertEqual(len(Receipt.objects.all()), 0)
        # Create a mock receipt image
        mock_image = SimpleUploadedFile("mock_image.jpg", b"image_content", "image/jpeg")

        data = {"receipt_name": "some name", "receipt_image": mock_image}
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self._receipts_api_create_url, data, **headers)
        self.assertEqual(len(Receipt.objects.all()), 1)
        self.assertIn("mock_image", Receipt.objects.first().image.name)
        self.assertTemplateUsed(response, "pages/receipts/_search_results.html")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Receipt added with the name of some name")

    def test_receipt_create_post_with_valid_but_no_name(self):
        # Test creating a receipt with a valid image but no name
        self.login_user()
        self.assertEqual(len(Receipt.objects.all()), 0)
        # Create a mock receipt image
        mock_image = SimpleUploadedFile("mock_image.jpg", b"image_content", "image/jpeg")
        data = {"receipt_name": "", "receipt_image": mock_image}
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self._receipts_api_create_url, data, **headers)
        self.assertEqual(len(Receipt.objects.all()), 1)
        self.assertTemplateUsed(response, "pages/receipts/_search_results.html")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Receipt added with the name of mock_image")

    def test_receipt_create_post_with_invalid_image(self):
        # Test creating a receipt with an invalid image
        self.login_user()
        data = {"receipt_name": "some name", "receipt_image": "not a valid image"}
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(self._receipts_api_create_url, data, **headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode("utf-8"), "No image found")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "No image found")
