import botocore.client
from botocore.config import Config
from botocore.exceptions import NoCredentialsError, PartialCredentialsError

from settings.helpers import get_var

import boto3
import logging

logger = logging.getLogger(__name__)

DEBUG_LEVEL = get_var("AWS_LOG_LEVEL", default="debug")
DEBUG_LEVEL = "debug" if DEBUG_LEVEL == "debug" else "info" if DEBUG_LEVEL == "info" else None


class Boto3Handler:
    def __init__(self):
        self.initiated: bool = False
        self.region_name: str = get_var("AWS_REGION_NAME", "eu-west-2")
        self.aws_access_key_id: str = get_var("AWS_ACCESS_KEY_ID")
        self.aws_access_key_secret: str = get_var("AWS_ACCESS_KEY")
        self.scheduler_lambda_arn: str = get_var("SCHEDULER_LAMBDA_ARN")
        self.scheduler_lambda_access_role_arn: str = get_var("SCHEDULER_LAMBDA_ACCESS_ROLE_ARN")
        self.scheduler_invoices_group_name: str = get_var("SCHEDULER_INVOICES_GROUP_NAME")
        self.dynamodb_client = None
        self.scheduler_client = None

        print(f"Region: {self.region_name}")
        print("| has aws access key id" if self.aws_access_key_id else "X no aws access key id")
        print("| has aws access key secret" if self.aws_access_key_secret else "X no aws access key secret")
        print("| has scheduler lambda arn" if self.scheduler_lambda_arn else "X no scheduler lambda arn")
        print(
            "| has scheduler lambda access role arn" if self.scheduler_lambda_access_role_arn else "X no scheduler lambda access role arn"
        )
        print("| has scheduler invoices group name" if self.scheduler_invoices_group_name else "X no scheduler invoices group name")

        self._initiate_clients()

    def _initiate_session(self):
        self._boto3_config = Config(region_name=self.region_name, signature_version="v4", retries={"max_attempts": 10, "mode": "standard"})

        self._boto3_session = boto3.Session(
            # aws_access_key_id=self.aws_access_key_id,
            # aws_secret_access_key=self.aws_access_key_secret,
            region_name=self.region_name
        )

        if DEBUG_LEVEL == "debug":
            boto3.set_stream_logger("", level=logging.DEBUG)
        else:
            boto3.set_stream_logger("", level=logging.INFO)

    def _initiate_clients(self):
        if get_var("AWS_DISABLED", "").lower() == "true":
            logger.info("The variable AWS_DISABLED is present, not initiating boto3")
            return

        if not get_var("AWS_ENABLED"):
            logger.error("The variable AWS_ENABLED is not present, not initiating boto3")
            return

        self._initiate_session()

        try:
            if not self._boto3_session.client("sts").get_caller_identity():
                logger.info("No AWS Credentials found, not initiating clients.")
                return
        except (NoCredentialsError, PartialCredentialsError) as error:
            logger.error(error)
            return None

        self._schedule_client = self._boto3_session.client("scheduler")
        self.schedule_client = self._schedule_client
        self._dynamodb_client = self._boto3_session.client("dynamodb")
        self.dynamodb_client = self._dynamodb_client

        self.SCHEDULE_EXCEPTIONS = self._schedule_client.exceptions
        self.DYNAMO_EXCEPTIONS = self._dynamodb_client.exceptions
        self.initiated = True

        logger.info("Boto3Handler has been initiated!")


BOTO3_HANDLER = Boto3Handler()
