from io import BytesIO

from PIL import Image
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import resolve, reverse
from datetime import date, timedelta

from backend.models import User, Team, Receipt, UserSettings, Invoice


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


@override_settings(STATICFILES_STORAGE="django.contrib.staticfiles.storage.StaticFilesStorage")
class ViewTestCase(TestCase):
    def setUp(self):
        self.log_in_user = User.objects.create_user(username="user@example.com", password="user", email="user@example.com")
        self.created_team = Team.objects.create(name="Testing", leader=self.log_in_user)
        self.created_team.members.add(self.log_in_user)
        self.htmx_headers = {"HTTP_HX-Request": "true"}

    def login_to_team(self):
        self.login_user()
        self.log_in_user.logged_in_as_team = self.created_team
        self.log_in_user.save()

    def tearDown(self):
        # Cleanup uploaded files
        Receipt.objects.all().delete()
        UserSettings.objects.all().delete()
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
