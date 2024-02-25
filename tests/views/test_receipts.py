import uuid

from django.contrib.messages import get_messages
from django.urls import reverse, resolve

from backend.models import Receipt, ReceiptDownloadToken
from tests.handler import ViewTestCase, create_mock_image


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
        self.assertEqual("backend.views.core.receipts.dashboard.receipts_dashboard", func_name)


class ReceiptsAPITestCase(ViewTestCase):
    def setUp(self):
        super().setUp()

        # Define URLs for the receipts API
        self._receipts_api_create_url = reverse("api:receipts:new")

    def test_receipt_create_post_with_valid(self):
        # Test creating a receipt with valid data
        self.login_user()
        self.assertEqual(len(Receipt.objects.all()), 0)
        # Create a mock receipt image
        mock_image = create_mock_image()

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
        mock_image = create_mock_image()
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


class ReceiptDownloadEndpointsTest(ViewTestCase):
    def setUp(self):
        super().setUp()
        self.receipt = Receipt.objects.create(user=self.log_in_user, image=create_mock_image())
        self.token = ReceiptDownloadToken.objects.create(user=self.log_in_user, file=self.receipt)
        self.download_receipt_url = reverse("api:receipts:download_receipt", args=[self.token.token])
        self.generate_download_link_url = reverse("api:receipts:generate_download_link", args=[self.receipt.id])

    def test_download_receipt_valid_token(self):
        self.login_user()
        response = self.client.get(self.download_receipt_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")

    def test_download_receipt_invalid_token(self):
        self.login_user()
        invalid_token = uuid.uuid4()  # Generate a valid UUID
        invalid_url = reverse("api:receipts:download_receipt", args=[invalid_token])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)  # Update expected status code

    def test_download_receipt_used_token(self):
        self.login_user()
        self.client.get(self.download_receipt_url)  # Use the token once
        response = self.client.get(self.download_receipt_url)  # Try to use the token again
        self.assertEqual(response.status_code, 404)  # Expect a 404 response

    def test_generate_download_link_valid_receipt(self):
        self.login_user()
        response = self.client.get(self.generate_download_link_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

    def test_generate_download_link_invalid_receipt(self):
        self.login_user()
        invalid_url = reverse("api:receipts:generate_download_link", args=[9999])  # Assuming 9999 is an invalid receipt id
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
