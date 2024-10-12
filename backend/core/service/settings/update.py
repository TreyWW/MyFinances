from backend.models import UserSettings
from PIL import Image

from backend.core.utils.dataclasses import BaseServiceResponse


class UpdateProfilePictureServiceResponse(BaseServiceResponse[str]): ...


def update_profile_picture(profile_picture, user_profile: UserSettings) -> UpdateProfilePictureServiceResponse:
    if not profile_picture:
        return UpdateProfilePictureServiceResponse(error_message="Invalid or unsupported image file")

    try:
        # Max file size is 10MB (Change the first number to determine the size in MB)
        max_file_size = 10 * 1024 * 1024

        if profile_picture.size is None:
            return UpdateProfilePictureServiceResponse(error_message="File size not found")

        if profile_picture.size > max_file_size:
            return UpdateProfilePictureServiceResponse(error_message="File size should be up to 10MB")

        img = Image.open(profile_picture)
        img.verify()

        if img.format is None or img.format.lower() not in ["jpeg", "png", "jpg"]:
            return UpdateProfilePictureServiceResponse(
                error_message="Unsupported image format. We support only JPEG, JPG, PNG, if you have a good extension, your file just got renamed."
            )

        user_profile.profile_picture = profile_picture
        user_profile.save()
        return UpdateProfilePictureServiceResponse(True, "Successfully updated profile picture")
    except (FileNotFoundError, Image.UnidentifiedImageError):
        return UpdateProfilePictureServiceResponse(error_message="Invalid or unsupported image file")
