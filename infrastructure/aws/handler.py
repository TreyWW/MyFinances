from __future__ import annotations

import logging
import sys

import boto3
from botocore.config import Config
from mypy_boto3_events.client import EventBridgeClient
from mypy_boto3_iam.client import IAMClient
from mypy_boto3_scheduler.client import EventBridgeSchedulerClient
from mypy_boto3_stepfunctions.client import SFNClient

from backend.models import FeatureFlags
from backend.utils.feature_flags import get_feature_status
from settings.helpers import get_var
from settings.settings import AWS_TAGS_APP_NAME

config = Config(connect_timeout=5, retries={"max_attempts": 2})

AWS_SCHEDULES_ENABLED = get_var("AWS_SCHEDULES_ACCESS_KEY_ID") and get_var("AWS_SCHEDULES_SECRET_ACCESS_KEY")

if not any(arg in sys.argv[1:] for arg in ["test", "migrate", "makemigrations"]):
    if not AWS_SCHEDULES_ENABLED and get_feature_status("isInvoiceSchedulingEnabled", should_use_cache=False):
        raise ValueError(
            "If using schedules, the variables MUST be set. If you are not going to use schedules, "
            "set the isInvoiceSchedulingEnabled feature flag to False. You can do so using the command \n"
            "`python manage.py feature_flags disable isInvoiceSchedulingEnabled`"
        )

    if not AWS_SCHEDULES_ENABLED and get_feature_status("areInvoiceRemindersEnabled", should_use_cache=False):
        raise ValueError(
            "If using schedules, the variables MUST be set. If you are not going to use schedules, "
            "set the areInvoiceRemindersEnabled feature flag to False. You can do so using the command \n"
            "`python manage.py feature_flags disable areInvoiceRemindersEnabled`"
        )

if AWS_SCHEDULES_ENABLED:
    Boto3HandlerSession = boto3.session.Session(
        aws_access_key_id=get_var("AWS_SCHEDULES_ACCESS_KEY_ID"),
        aws_secret_access_key=get_var("AWS_SCHEDULES_SECRET_ACCESS_KEY"),
        region_name=get_var("AWS_SCHEDULES_REGION_NAME", default="eu-west-2"),
    )

    event_bridge_client: EventBridgeClient = Boto3HandlerSession.client("events")
    event_bridge_scheduler: EventBridgeSchedulerClient = Boto3HandlerSession.client("scheduler", config=config)
    iam_client: IAMClient = Boto3HandlerSession.client("iam", config=config)
    sfn_client: SFNClient = Boto3HandlerSession.client("stepfunctions", config=config)


def get_event_bridge_client():
    if not AWS_SCHEDULES_ENABLED:
        raise ValueError("If using schedules, the variables MUST be set.")
    return event_bridge_client


def get_event_bridge_scheduler():
    if not AWS_SCHEDULES_ENABLED:
        raise ValueError("If using schedules, the variables MUST be set.")
    return event_bridge_scheduler


def get_iam_client():
    if not AWS_SCHEDULES_ENABLED:
        raise ValueError("If using schedules, the variables MUST be set.")
    return iam_client


def get_sfn_client():
    if not AWS_SCHEDULES_ENABLED:
        raise ValueError("If using schedules, the variables MUST be set.")
    return sfn_client


DEBUG_LEVEL = get_var("AWS_PRINT_DEBUG_LEVEL", default="debug")
DEBUG_LEVEL = "debug" if DEBUG_LEVEL == "debug" else "info" if DEBUG_LEVEL == "info" else None

if get_var("LOG_LEVEL", default="info") == "debug":
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)

logger = logging.getLogger()

if DEBUG_LEVEL == "debug":
    boto3.set_stream_logger("", level=logging.DEBUG)
else:
    boto3.set_stream_logger("", level=logging.INFO)

APP_TAGS = [{"key": "app", "value": AWS_TAGS_APP_NAME}]
