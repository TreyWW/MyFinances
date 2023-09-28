from django.urls import reverse


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