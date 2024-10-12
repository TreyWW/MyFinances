import uuid
from django.core.management.base import BaseCommand
from backend.core.api.public import APIAuthToken


class Command(BaseCommand):
    """
    Generates an API key for the AWS EventBridge API.
    """

    def handle(self, *args, **kwargs):
        token = APIAuthToken(service=APIAuthToken.AdministratorServiceTypes.AWS_API_DESTINATION, name=str(uuid.uuid4()))
        raw_key: str = token.generate_key()
        token.save()

        self.stdout.write(
            f"""
        NOTE: Keep this key secret. It is used to authenticate your API requests with the AWS EventBridge API.

        Your API Key: {raw_key}

        To use this API Key for development you can use:

        pulumi config set api_destination-api_key {raw_key}
        pulumi up

        If you would like to use it for production use:
        pulumi stack select production
        pulumi config set api_destination-api_key {raw_key}
        pulumi up
        """
        )
