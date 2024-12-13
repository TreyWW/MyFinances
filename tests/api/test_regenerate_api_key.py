from django.test import TestCase
from django.urls import reverse
from backend.models import User
from backend.core.api.public import APIAuthToken


class RegenerateAPIKeyTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user@example.com",
            password="user",
            email="user@example.com",
            entitlements=["api-access", "api_keys:write"],
            is_superuser=False,
        )
        self.user.save()
        self.client.login(username="user@example.com", password="user")
        self.api_key = APIAuthToken.objects.create(
            user=self.user, name="Test Key", scopes=["api_keys:write"], description="Test Description"
        )
        self.url = reverse("api:settings:api_keys regenerate", args=[self.api_key.id])

    def test_regenerate_api_key_success(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API key regenerated successfully")
        self.assertTrue(APIAuthToken.objects.filter(name="Test Key").exists())

    def test_regenerate_nonexistent_api_key(self):
        invalid_url = reverse("api:settings:api_keys regenerate", args=[999999])
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "API key not found")

    def test_regenerate_api_key_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def tearDown(self):
        APIAuthToken.objects.all().delete()
        self.user.delete()
