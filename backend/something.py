from django.test import TestCase
from django.urls import reverse


class TestUrls(TestCase):
    def test_dashboard(self):
        dashboard_url = reverse('dashboard')
        response = self.client.get(dashboard_url)
        self.assertEqual(response.status_code, 200)