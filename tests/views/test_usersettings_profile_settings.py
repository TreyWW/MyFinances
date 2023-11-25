import os

from django.urls import reverse
from backend.models import UserSettings
from tests.handler import ViewTestCase
from django.contrib.messages import get_messages
from model_bakery import baker
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


class UserSettingsProfileSettingsViewTestCase(ViewTestCase):
    def test_usersettings_profile_picture_post_with_valid(self):
        # Log in the user
        self.login_user()

        # Check default user settings
        response = self.client.get(reverse("user settings"))
        usr_settings = UserSettings.objects.first()
        self.assertIsNotNone(usr_settings)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["user_settings"], usr_settings)
        self.assertEqual(response.context["user_settings"].profile_picture_url, "")

        # Change profile picture and recheck
        headers = {"HTTP_HX-Request": "true"}
        mock_image = create_mock_image()
        response = self.client.post(
            reverse("user settings"),
            {
                "profile_image": mock_image,
                "section": "profile_picture",
            },
            **headers,
        )
        self.assertEqual(response.status_code, 200)

        # Check that only the message "Successfully updated profile picture" is returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Successfully updated profile picture")

        # Check that the user's profile picture URL is updated in the response
        expected_profile_picture_filename = os.path.basename(mock_image.name)
        expected_profile_picture_filename = expected_profile_picture_filename[
            :-4
        ]  # Remove .jpg suffix
        self.assertIn(
            expected_profile_picture_filename,
            response.context["users_profile_picture"],
        )

    def test_usersettings_profile_picture_post_with_invalid(self):
        # Log in the user
        self.login_user()

        # Provide htmx in request
        headers = {"HTTP_HX-Request": "true"}
        response = self.client.post(
            reverse("user settings"),
            {"profile_image": "invalid", "section": "profile_picture"},
            **headers,
        )

        # Check that only the message "Invalid or unsupported image file" is returned
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Invalid or unsupported image file")

        # Check that the response is successful
        self.assertEqual(response.status_code, 200)

        # Check that the profile picture is still at default and hasn't changed
        self.assertEqual(response.context["users_profile_picture"], "")
