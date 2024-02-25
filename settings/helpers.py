import os
from typing import Union, List

import boto3
import environ
from django_ratelimit.core import get_usage
from mypy_boto3_sesv2.client import SESV2Client

### NEEDS REFACTOR

env = environ.Env(DEBUG=(bool, False))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))
env = environ.Env()
environ.Env.read_env()


def get_var(key, default=None, required=False):
    value = os.environ.get(key, default=default)

    if required and not value:
        raise ValueError(f"{key} is required")
    if not default and not value:  # So methods like .lower() don't error
        value = ""
    return value


def increment_rate_limit(request, group):
    """
    Alias of is_ratelimited that just increments the rate limit for the given group.

    Returns the new usage count.
    """
    usage = get_usage(request, group, increment=True)
    return usage.get("count", 0)


EMAIL_CLIENT: SESV2Client = boto3.client(
    "sesv2",
    region_name="eu-west-2",
    aws_access_key_id=get_var("AWS_SES_ACCESS_KEY_ID"),
    aws_secret_access_key=get_var("AWS_SES_SECRET_ACCESS_KEY"),
)

AWS_SES_ACCESS_KEY_ID = get_var("AWS_SES_ACCESS_KEY_ID")
AWS_SES_SECRET_ACCESS_KEY = get_var("AWS_SES_SECRET_ACCESS_KEY")
ARE_AWS_EMAILS_ENABLED = True if AWS_SES_ACCESS_KEY_ID and AWS_SES_SECRET_ACCESS_KEY else False

SENDGRID_TEMPLATE = get_var("SENDGRID_TEMPLATE")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_HOST_USER = "apikey"
EMAIL_FROM_ADDRESS = get_var("SENDGRID_FROM_ADDRESS")
EMAIL_HOST_PASSWORD = get_var("SENDGRID_API_KEY")
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_SERVER_ENABLED = True if EMAIL_HOST_PASSWORD else False

EMAIL_SERVICE = "SES" if ARE_AWS_EMAILS_ENABLED else "SendGrid" if EMAIL_SERVER_ENABLED else None
ARE_EMAILS_ENABLED = True if EMAIL_SERVICE else False


def send_email(destination: Union[str, List[str]], subject: str, message: str):
    """
    Args:
    destination (email addr or list of email addr): The email address or list of email addresses to send the
    email to.
    subject (str): The subject of the email.
    message (str): The content of the email.
    """
    if EMAIL_SERVICE == "SES":
        if not isinstance(destination, list):
            destination = [destination]
        return EMAIL_CLIENT.send_email(
            FromEmailAddress=get_var("AWS_SES_FROM_ADDRESS"),
            Destination={"ToAddresses": destination},
            Content={
                "Simple": {
                    "Subject": {"Data": subject},
                    "Body": {"Text": {"Data": message}},
                }
            },
        )
    # TODO: Add sendgrid emails
