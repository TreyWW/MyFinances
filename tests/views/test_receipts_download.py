import os
import shutil
import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase

from backend.models import Receipt, ReceiptDownloadToken, User


class ReceiptDownloadEndpointsTest(TestCase):
    @classmethod
    def tearDownClass(cls):
        directory = "media/private/receipts"
        try:
            shutil.rmtree(directory)
            os.mkdir(directory)
        except PermissionError:
            print(
                '"ReceiptDownloadEndpointsTest" tearDownClass() failed due to random PermissionError '
                "(only on Windows). Files in /media/private/receipts have not been deleted. Run tests again to delete files."
            )
        super().tearDownClass()

    def setUp(self):
        super().setUp()
        self.log_in_user = User.objects.create_user(username="test@example.com", password="user", email="test@example.com")
        self.client.login(username="test@example.com", password="user")

        self.receipt = Receipt.objects.create(
            user=self.log_in_user, image=SimpleUploadedFile("mock_image.jpg", b"image_content", "image/jpeg")
        )
        self.token = ReceiptDownloadToken.objects.create(user=self.log_in_user, file=self.receipt)
        self.download_receipt_url = reverse("api:finance:receipts:download_receipt", args=[self.token.token])
        self.generate_download_link_url = reverse("api:finance:receipts:generate_download_link", args=[self.receipt.id])

    def test_download_receipt_valid_token(self):
        response = self.client.get(self.download_receipt_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/jpeg")

    def test_download_receipt_invalid_token(self):
        invalid_token = uuid.uuid4()  # Generate a valid UUID
        invalid_url = reverse("api:finance:receipts:download_receipt", args=[invalid_token])
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)  # Update expected status code

    def test_download_receipt_used_token(self):
        self.client.get(self.download_receipt_url)  # Use the token once
        response = self.client.get(self.download_receipt_url)  # Try to use the token again
        self.assertEqual(response.status_code, 404)  # Expect a 404 response

    def test_generate_download_link_valid_receipt(self):
        response = self.client.get(self.generate_download_link_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.client.logout()

    def test_generate_download_link_invalid_receipt(self):
        invalid_url = reverse("api:finance:receipts:generate_download_link", args=[9999])  # Assuming 9999 is an invalid receipt id
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, 404)
        self.client.logout()

    def test_download_receipt_user_mismatch(self):
        another_user = User.objects.create_user(username="user@example.com", password="anotherpassword", email="user@example.com")
        another_token = ReceiptDownloadToken.objects.create(user=another_user, file=self.receipt)
        self.client.login(username="user@example.com", password="user")

        download_receipt_url = reverse("api:finance:receipts:download_receipt", args=[another_token.token])
        response = self.client.get(download_receipt_url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.content, b"Forbidden")
