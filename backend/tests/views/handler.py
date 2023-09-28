from django.urls import reverse
from django.test import TestCase
from backend.models import User


class ViewTestCase(TestCase):
    def setUp(self):
        User.objects.create_user(username="user", password="user")

    def call_index(self):
        self.client.get(reverse("index"))


def login_user(self):
    self.client.login(username="user", password="user")


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
