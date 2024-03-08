import boto3
from mypy_boto3_events.client import EventBridgeClient
from mypy_boto3_iam.client import IAMClient
from mypy_boto3_scheduler.client import EventBridgeSchedulerClient
from mypy_boto3_stepfunctions.client import SFNClient

from settings.helpers import get_var
from settings.settings import AWS_TAGS_APP_NAME

EventBridgeSession = boto3.session.Session(
    aws_access_key_id=get_var("AWS_SCHEDULES_ACCESS_KEY_ID"),
    aws_secret_access_key=get_var("AWS_SCHEDULES_SECRET_ACCESS_KEY"),
    region_name=get_var("AWS_SCHEDULES_REGION_NAME", default="eu-west-2"),
)

event_bridge_client: EventBridgeClient = EventBridgeSession.client("events")
event_bridge_scheduler: EventBridgeSchedulerClient = EventBridgeSession.client("scheduler")
iam_client: IAMClient = EventBridgeSession.client("iam")
sfn_client: SFNClient = EventBridgeSession.client("stepfunctions")

DEBUG_LEVEL = get_var("AWS_PRINT_DEBUG_LEVEL", default="debug")
DEBUG_LEVEL = "debug" if DEBUG_LEVEL == "debug" else "info" if DEBUG_LEVEL == "info" else None

APP_TAGS = [{
    "key": "app",
    "value": AWS_TAGS_APP_NAME
}]
