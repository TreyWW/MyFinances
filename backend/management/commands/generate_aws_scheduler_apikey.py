from django.core.management.base import BaseCommand

from backend.models import APIKey


class Command(BaseCommand):
    """
    Generates an API key for the AWS EventBridge API.
    """

    def handle(self, *args, **kwargs):
        token = APIKey.objects.create(service=APIKey.ServiceTypes.AWS_API_DESTINATION)
        key = f"{token.id}:{token.key}"
        token.hash()

        self.stdout.write(
            f"""
        NOTE: Keep this key secret. It is used to authenticate your API requests with the AWS EventBridge API.

        Your API Key: {key}

        To use this API Key for development you can use:

        pulumi config set api_destination-api_key {key}
        pulumi up

        If you would like to use it for production use:
        pulumi stack select production
        pulumi config set api_destination-api_key {key}
        pulumi up
        """
        )
