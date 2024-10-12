import json
import os

from django.test import TestCase
from django.urls import reverse

from backend.models import User


class UrlTestCase(TestCase):
    was_logged_in = False

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        # self.customer = Clients.objects.create(id=1, name="Test Customer")

    def load_json_data(self, filename):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, filename)
        with open(json_path, "r") as file:
            return json.load(file)

    def test_urls(self):
        unlogged_in_data = self.load_json_data("unlogged_in.json")
        for url_name, status_codes in unlogged_in_data.items():
            url = reverse(url_name, args=status_codes[1:])
            self._test_url(url, url_name, status_codes)

    def _test_url(self, url, url_name, status_codes):
        response = self.client.get(url)
        expected_status_code = status_codes[0] if status_codes else 200
        star = "***" if expected_status_code != response.status_code else ""

        print(f"{star}  Testing URL (Logged Out) - {url} || exp: {expected_status_code} - actual: {response.status_code}")
        self.assertEqual(response.status_code, expected_status_code)

    def test_logged_in_urls(self):
        # Log in the client
        self.client.login(username="testuser", password="testpassword")

        # Test the logged-in URLs
        logged_in_data = self.load_json_data("logged_in.json")
        for url_name, status_codes in logged_in_data.items():
            url = reverse(url_name, args=status_codes[1:])
            self._test_logged_in_url(url, url_name, status_codes)

        # Log out the client
        self.client.logout()

    def _test_logged_in_url(self, url, url_name, status_codes):
        self.client.login(username="testuser", password="testpassword")
        response = self.client.get(url)
        expected_status_code = status_codes[0] if status_codes else 200
        star = "***" if expected_status_code != response.status_code else ""

        print(f"{star}  Testing URL (Logged In) - {url} || exp: {expected_status_code} - actual: {response.status_code}")

        if expected_status_code != response.status_code:
            print("Response Content Type:", response.get("Content-Type"))
            print("Response Headers:", response.headers)
            print("Response Content:")
            print(response.content)  # Print the response content for debugging

        # try:
        self.assertEqual(response.status_code, expected_status_code)
        # except AssertionError:
        #     pass
