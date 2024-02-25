from io import BytesIO

from PIL import Image
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, SimpleTestCase
from django.urls import resolve, reverse

from backend.models import User, Receipt, UserSettings


def assert_url_matches_view(url_path, url_name, view_function_path):
    """
    Assert that the given URL name matches the specified view function.

    Args:
        url_path (str): The full URL path of the view. (e.g. api//clients/fetch/)
        url_name (str): The name of the URL to reverse. (e.g. api:clients:fetch)
        view_function_path (str): The expected path of the view function (e.g., "backend.api.clients.fetch.fetch_all_clients").
    """
    resolved_func = resolve(url_path).func
    resolved_func_name = f"{resolved_func.__module__}.{resolved_func.__name__}"

    SimpleTestCase().assertEqual(reverse(url_name), url_path)
    SimpleTestCase().assertEqual(resolved_func_name, view_function_path)


def create_mock_image():
    """
    Create a simple mock image using Pillow.

    Returns:
        SimpleUploadedFile: A mock image as a SimpleUploadedFile.
    """
    image = Image.new("RGB", (100, 100), "white")
    image_io = BytesIO()
    image.save(image_io, "JPEG")
    return SimpleUploadedFile("mock_image.jpg", image_io.getvalue(), content_type="image/jpeg")


def cleanup_uploaded_files(files):
    """
    Cleanup uploaded files.

    Args:
        files (list): List of files to delete.
    """
    [file.delete() for file in files]


class ViewTestCase(TestCase):
    def setUp(self):
        self.log_in_user = User.objects.create_user(username="user@example.com", password="user", email="user@example.com")
        self.mock_images = []
        self.htmx_headers = {"HTTP_HX-Request": "true"}

    def tearDown(self):
        # Cleanup uploaded files
        cleanup_uploaded_files(self.mock_images)
        cleanup_uploaded_files([receipt.image for receipt in Receipt.objects.all()])
        cleanup_uploaded_files([pfp.profile_picture for pfp in UserSettings.objects.all()])
        super().tearDown()

    def call_index(self):
        self.client.get(reverse("index"))

    def login_user(self):
        self.client.login(username="user@example.com", password="user")

    def make_request(self, method="get", data=None, with_htmx=True, format=None):
        """
        Makes request to self.url_name, defaults "with htmx"
        """
        headers = self.htmx_headers if with_htmx else {}
        method = method.lower() or "get"
        if method == "post":
            return self.client.post(reverse(self.url_name), data, **headers)
        elif method == "delete":
            return self.client.delete(reverse(self.url_name), data, **headers)
        else:
            return self.client.get(reverse(self.url_name), **headers)

    def get_all_messages(self, response):
        try:
            return list(get_messages(response.wsgi_request))
        except:
            return []
