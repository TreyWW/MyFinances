from dataclasses import dataclass
from botocore.config import Config

from settings.helpers import get_var

import boto3
import logging

logger = logging.getLogger(__name__)


class Boto3Handler:
    def __init__(self):
        self.initiated: bool = False
        self.region_name: str = get_var("AWS_REGION_NAME")
        self.aws_access_key_id: str = get_var("AWS_ACCESS_KEY_ID")
        self.aws_access_key_secret: str = get_var("AWS_ACCESS_KEY")
        self.scheduler_lambda_arn: str = get_var("SCHEDULER_LAMBDA_ARN")
        self.scheduler_lambda_access_role_arn: str = get_var("SCHEDULER_LAMBDA_ACCESS_ROLE_ARN")
        self.scheduler_invoices_group_name: str = get_var("SCHEDULER_INVOICES_GROUP_NAME")

        self._initiate_clients()

    def _initiate_session(self):
        self._boto3_config = Config(region_name=self.region_name, signature_version="v4", retries={"max_attempts": 10, "mode": "standard"})

        self._boto3_session = boto3.Session(
            aws_access_key_id=self.aws_access_key_id, aws_secret_access_key=self.aws_access_key_secret, region_name=self.region_name
        )

    def _initiate_clients(self):
        if not get_var("AWS_ACCESS_KEY_ID") or not get_var("AWS_ACCESS_KEY") or get_var("AWS_DISABLED"):
            logger.info("AWS credentials not provided")
            return

        self._initiate_session()

        self._schedule_client = self._boto3_session.client("scheduler")
        self.initiated = True


BOTO3_HANDLER = Boto3Handler()
