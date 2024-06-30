from backend.models import UserSettings
from PIL import Image


def update_profile_picture(profile_picture, user_profile: UserSettings) -> tuple[bool, str]:
    if not profile_picture:
        return False, "Invalid or unsupported image file"

    try:
        # Max file size is 10MB (Change the first number to determine the size in MB)
        max_file_size = 10 * 1024 * 1024

        if profile_picture.size is None:
            return False, "File size not found"

        if profile_picture.size > max_file_size:
            return False, "File size should be up to 10MB."

        img = Image.open(profile_picture)
        img.verify()

        if img.format is None or img.format.lower() not in ["jpeg", "png", "jpg"]:
            return False, "Unsupported image format. We support only JPEG, JPG, PNG."

        user_profile.profile_picture = profile_picture
        user_profile.save()
        return True, "Successfully updated profile picture"
    except (FileNotFoundError, Image.UnidentifiedImageError):
        return False, "Invalid or unsupported image file"
