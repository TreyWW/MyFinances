from django.core.management.base import BaseCommand

from backend.models import APIKey


class Command(BaseCommand):
    """
    Generates an API key for the AWS EventBridge API.
    """

    def handle(self, *args, **kwargs):
        token = APIKey.objects.create(service=APIKey.ServiceTypes.AWS_API_DESTINATION)
        key = f"{token.id}{token.key}"
        token.hash()

        self.stdout.write(f"""
        NOTE: Keep this key secret. It is used to authenticate your API requests with the AWS EventBridge API.
        
        Your API Key: {key}
        
        You should put this key under "/infrastructure/aws/terraform/terraform.tfvars" and then add this line: 
        
        api_destination-api_key = "{key}"
        """)
