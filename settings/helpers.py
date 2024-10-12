from __future__ import annotations

import json
import os
import sys
from logging import exception

import boto3
import environ
from django_ratelimit.core import get_usage
from mypy_boto3_sesv2.client import SESV2Client
from mypy_boto3_sesv2.type_defs import (
    SendEmailResponseTypeDef,
    BulkEmailEntryTypeDef,
    SendBulkEmailResponseTypeDef,
)

from backend.core.types.emails import (
    SingleEmailInput,
    BulkTemplatedEmailInput,
    SingleTemplatedEmailContent,
    SingleEmailSendServiceResponse,
    BulkEmailSendServiceResponse,
    BulkEmailEmailItem,
)

# NEEDS REFACTOR

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
    # aws_access_key_id=get_var("AWS_SES_ACCESS_KEY_ID"),
    # aws_secret_access_key=get_var("AWS_SES_SECRET_ACCESS_KEY"),
)

# AWS_SES_ACCESS_KEY_ID = get_var("AWS_SES_ACCESS_KEY_ID")
# AWS_SES_SECRET_ACCESS_KEY = get_var("AWS_SES_SECRET_ACCESS_KEY")
AWS_SES_FROM_ADDRESS = get_var("AWS_SES_FROM_ADDRESS")
ARE_AWS_EMAILS_ENABLED = (True if get_var("AWS_SES_ENABLED", "").lower() == "true" else False) and AWS_SES_FROM_ADDRESS

# SENDGRID_TEMPLATE = get_var("SENDGRID_TEMPLATE")
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
# EMAIL_HOST = "smtp.sendgrid.net"
# EMAIL_HOST_USER = "apikey"
# EMAIL_FROM_ADDRESS = get_var("SENDGRID_FROM_ADDRESS")
# EMAIL_HOST_PASSWORD = get_var("SENDGRID_API_KEY")
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_SERVER_ENABLED = True if EMAIL_HOST_PASSWORD else False

EMAIL_SERVICE = "SES" if ARE_AWS_EMAILS_ENABLED else None
ARE_EMAILS_ENABLED = True if EMAIL_SERVICE else False

if "test" in sys.argv[1:]:
    ARE_EMAILS_ENABLED = False


def send_email(
    destination: str | list[str],
    subject: str | None,
    content: str | SingleTemplatedEmailContent,
    ConfigurationSetName: str | None = None,
    from_address: str | None = None,
    from_address_name_prefix: str | None = None,
) -> SingleEmailSendServiceResponse:
    """
    Args:
    destination (email addr or list of email addr): The email address or list of email addresses to send the
    email to.
    subject (str): The subject of the email.
    message (str): The content of the email.
    """

    data = SingleEmailInput(
        destination=destination,
        subject=subject,
        content=content,
        ConfigurationSetName=ConfigurationSetName,
        from_address=from_address,
        from_address_name_prefix=from_address_name_prefix,
    )

    if get_var("DEBUG", "").lower() == "true":
        if not "test" in sys.argv[1:]:
            print(data)
        return SingleEmailSendServiceResponse(
            True,
            response=SendEmailResponseTypeDef(
                MessageId="",
                ResponseMetadata={
                    "RequestId": "",
                    "HTTPStatusCode": 200,
                    "HTTPHeaders": {},
                    "RetryAttempts": 0,
                    "HostId": "",
                },
            ),
        )

    if EMAIL_SERVICE == "SES":
        if not isinstance(data.destination, list):
            data.destination = [data.destination]

        response: SendEmailResponseTypeDef | None = None

        try:
            if isinstance(data.content, dict):
                data_str = (
                    data.content.get("template_data")
                    if isinstance(data.content.get("template_data"), str)
                    else json.dumps(data.content.get("template_data"))
                )

                from_email_address: str = str(data.from_address_name_prefix) if data.from_address_name_prefix else ""
                from_email_address += str(data.from_address or AWS_SES_FROM_ADDRESS)

                response = EMAIL_CLIENT.send_email(
                    FromEmailAddress=from_email_address,
                    Destination={"ToAddresses": data.destination},
                    Content={"Template": {"TemplateName": data.content.get("template_name"), "TemplateData": data_str}},  # type: ignore
                    ConfigurationSetName=data.ConfigurationSetName or "",
                )
            else:
                from_email_address = str(data.from_address_name_prefix) if data.from_address_name_prefix else ""
                from_email_address += str(data.from_address or AWS_SES_FROM_ADDRESS)

                response = EMAIL_CLIENT.send_email(
                    FromEmailAddress=from_email_address,
                    Destination={"ToAddresses": data.destination},
                    Content={
                        "Simple": {"Subject": {"Data": data.subject if data.subject else ""}, "Body": {"Text": {"Data": data.content}}}
                    },
                    ConfigurationSetName=data.ConfigurationSetName or "",
                )
            return SingleEmailSendServiceResponse(True, response=response)
        except EMAIL_CLIENT.exceptions.MessageRejected:
            return SingleEmailSendServiceResponse(error_message="Email rejected", response=response)

        except EMAIL_CLIENT.exceptions.AccountSuspendedException:
            return SingleEmailSendServiceResponse(error_message="Email account suspended", response=response)

        except EMAIL_CLIENT.exceptions.SendingPausedException:
            return SingleEmailSendServiceResponse(error_message="Email sending paused", response=response)

        except Exception as error:
            exception(f"Unexpected error occurred: {error}")
            return SingleEmailSendServiceResponse(error_message="Email service error", response=response)
    return SingleEmailSendServiceResponse(error_message="No email service configured")


def send_bulk_email(
    email_list: list[BulkEmailEmailItem],
    ConfigurationSetName: str | None = None,
    from_address: str | None = None,
) -> BulkEmailSendServiceResponse:

    entries: list[BulkEmailEntryTypeDef] = [
        {
            "Destination": {
                "ToAddresses": [entry.destination] if not isinstance(entry.destination, list) else entry.destination,
                "CcAddresses": entry.cc,
                "BccAddresses": entry.bcc,
            }
        }
        for entry in email_list
    ]

    try:
        response: SendBulkEmailResponseTypeDef = EMAIL_CLIENT.send_bulk_email(
            FromEmailAddress=from_address or AWS_SES_FROM_ADDRESS,
            BulkEmailEntries=entries,
            ConfigurationSetName=ConfigurationSetName or "",
            DefaultContent={},
        )

        return BulkEmailSendServiceResponse(True, response=response)
    except EMAIL_CLIENT.exceptions.MessageRejected:
        return BulkEmailSendServiceResponse(error_message="Email rejected", response=locals().get("response", None))

    except EMAIL_CLIENT.exceptions.AccountSuspendedException:
        return BulkEmailSendServiceResponse(error_message="Email account suspended", response=locals().get("response", None))

    except EMAIL_CLIENT.exceptions.SendingPausedException:
        return BulkEmailSendServiceResponse(error_message="Email sending paused", response=locals().get("response", None))

    except Exception as error:
        exception(f"Unexpected error occurred: {error}")
        return BulkEmailSendServiceResponse(error_message="Email service error", response=locals().get("response", None))


def send_templated_bulk_email(
    email_list: list[BulkEmailEmailItem],
    template_name: str,
    default_template_data: dict | str,
    ConfigurationSetName: str | None = None,
    from_address: str | None = None,
    from_address_name_prefix: str | None = None,
) -> BulkEmailSendServiceResponse:

    data = BulkTemplatedEmailInput(
        email_list=email_list,
        template_name=template_name,
        default_template_data=default_template_data,
        ConfigurationSetName=ConfigurationSetName,
        from_address=from_address,
        from_address_name_prefix=from_address_name_prefix,
    )

    entries: list[BulkEmailEntryTypeDef] = []

    for entry in data.email_list:
        destination: list[str] = [entry.destination] if not isinstance(entry.destination, list) else entry.destination

        data_str: str = entry.template_data if isinstance(entry.template_data, str) else json.dumps(entry.template_data)

        entries.append(
            {
                "Destination": {"ToAddresses": destination, "CcAddresses": entry.cc, "BccAddresses": entry.bcc},
                "ReplacementEmailContent": {"ReplacementTemplate": {"ReplacementTemplateData": data_str}},
            }
        )

    try:
        data_str = data.default_template_data if isinstance(data.default_template_data, str) else json.dumps(data.default_template_data)
        from_email_address: str = str(data.from_address_name_prefix) if data.from_address_name_prefix else ""
        from_email_address += str(data.from_address or AWS_SES_FROM_ADDRESS)

        response: SendBulkEmailResponseTypeDef = EMAIL_CLIENT.send_bulk_email(
            FromEmailAddress=from_email_address,
            BulkEmailEntries=entries,
            ConfigurationSetName=data.ConfigurationSetName or "",
            DefaultContent={"Template": {"TemplateName": data.template_name, "TemplateData": data_str}},
        )
        return BulkEmailSendServiceResponse(True, response=response)
    except EMAIL_CLIENT.exceptions.MessageRejected:
        return BulkEmailSendServiceResponse(error_message="Email rejected", response=locals().get("response", None))

    except EMAIL_CLIENT.exceptions.AccountSuspendedException:
        return BulkEmailSendServiceResponse(error_message="Email account suspended", response=locals().get("response", None))

    except EMAIL_CLIENT.exceptions.SendingPausedException:
        return BulkEmailSendServiceResponse(error_message="Email sending paused", response=locals().get("response", None))

    except Exception as error:
        exception(f"Unexpected error occurred: {error}")
        return BulkEmailSendServiceResponse(error_message="Email service error", response=locals().get("response", None))


if not any(arg in sys.argv[1:] for arg in ["test", "migrate", "makemigrations"]):
    if not get_var("SITE_URL"):
        raise ValueError("SITE_URL is required")

    if not get_var("SITE_NAME"):
        raise ValueError("SITE_NAME is required")
