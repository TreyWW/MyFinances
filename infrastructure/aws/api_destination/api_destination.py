from mypy_boto3_events.type_defs import CreateApiDestinationResponseTypeDef, DescribeApiDestinationResponseTypeDef

from backend.models import APIKey
from settings.settings import AWS_TAGS_APP_NAME, SITE_URL
from ..handler import get_event_bridge_client


def get_or_create_api_destination() -> CreateApiDestinationResponseTypeDef | DescribeApiDestinationResponseTypeDef:
    event_bridge_client = get_event_bridge_client()
    try:
        print("[AWS] [API_D] Describing API Destination...", flush=True)
        response = event_bridge_client.describe_api_destination(Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices")

        if response.get("ApiDestinationState") == "INACTIVE":
            connection_arn = get_or_create_api_connection_arn()
            print("[AWS] [API_D] Updating API Destination with updated connection...", flush=True)
            event_bridge_client.update_api_destination(Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices", ConnectionArn=connection_arn)
        response = event_bridge_client.describe_api_destination(Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices")
        return response
    except event_bridge_client.exceptions.ResourceNotFoundException:
        connection_arn = get_or_create_api_connection_arn()
        return event_bridge_client.create_api_destination(
            Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices",
            Description="MyFinances Scheduled Invoices",
            ConnectionArn=connection_arn,
            HttpMethod="POST",
            InvocationEndpoint=f"{SITE_URL}/api/invoices/schedules/receive/",
        )


def get_or_create_api_connection_arn() -> str:
    event_bridge_client = get_event_bridge_client()
    try:
        response = event_bridge_client.describe_connection(Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices").get("ConnectionArn")
        return response
    except event_bridge_client.exceptions.ResourceNotFoundException:
        token = APIKey.objects.create(service=APIKey.ServiceTypes.AWS_API_DESTINATION)
        key = f"{token.id}:{token.key}"
        token.hash()

        print(key)

        return event_bridge_client.create_connection(
            Name=f"{AWS_TAGS_APP_NAME}-scheduled-invoices",
            Description="MyFinances Scheduled Invoices",
            AuthorizationType="API_KEY",
            AuthParameters={"ApiKeyAuthParameters": {"ApiKeyName": "Authorization", "ApiKeyValue": f"Token {key}"}},
        ).get("ConnectionArn")
