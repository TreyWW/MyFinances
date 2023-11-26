from django.urls import reverse
from django.test import TestCase
from backend.models import User, Receipt, UserSettings
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from io import BytesIO


def create_mock_image():
    """
    Create a simple mock image using Pillow.

    Returns:
        SimpleUploadedFile: A mock image as a SimpleUploadedFile.
    """
    image = Image.new("RGB", (100, 100), "white")
    image_io = BytesIO()
    image.save(image_io, "JPEG")
    return SimpleUploadedFile(
        "mock_image.jpg", image_io.getvalue(), content_type="image/jpeg"
    )


class ViewTestCase(TestCase):
    def setUp(self):
        self.log_in_user = User.objects.create_user(
            username="user@example.com", password="user", email="user@example.com"
        )
        self.mock_images = []

    def tearDown(self):
        [image.delete() for image in self.mock_images]
        [receipt.image.delete() for receipt in Receipt.objects.all()]
        [pfp.profile_picture.delete() for pfp in UserSettings.objects.all()]
        super().tearDown()

    def call_index(self):
        self.client.get(reverse("index"))

    def login_user(self):
        self.client.login(username="user@example.com", password="user")


def test_with_prints(self, url, expected_status_code, logged_in):
    url = reverse(url)
    print("-----------------------")
    print(f"({'NL' if not logged_in else 'LI'}) Testing {url}")
    print(f"Expected: {expected_status_code}")
    if logged_in:
        login_user(self)
    response = self.client.get(url)
    print("Actual: ", response.status_code)
    self.assertEqual(response.status_code, expected_status_code)
    print("-----------------------")
