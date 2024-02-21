import os
from typing import Union, List

import boto3
import environ
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


EMAIL_CLIENT: SESV2Client = boto3.client("sesv2",
                                         region_name="eu-west-2",
                                         aws_access_key_id=get_var("AWS_SES_ACCESS_KEY_ID"),
                                         aws_secret_access_key=get_var("AWS_SES_SECRET_ACCESS_KEY"))

ARE_EMAILS_ENABLED = get_var("AWS_SES_ACCESS_KEY_ID") and get_var("AWS_SES_SECRET_ACCESS_KEY")


def send_email(destination: Union[str, List[str]], subject: str, message: str):
    if not isinstance(destination, list):
        destination = [destination]
    return EMAIL_CLIENT.send_email(
        FromEmailAddress=get_var("AWS_SES_FROM_ADDRESS"),
        Destination={
            "ToAddresses": destination
        },
        Content={
            "Simple": {
                "Subject": {
                    "Data": subject
                },
                "Body": {
                    "Text": {
                        "Data": message
                    }
                }
            }
        }
    )