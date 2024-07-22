import json
import os
import logging
import uuid

import boto3
from botocore.config import Config

config = Config(connect_timeout=5, retries={"max_attempts": 2})

Boto3HandlerSession = boto3.session.Session(
    aws_access_key_id=os.environ.get("AWS_SCHEDULES_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SCHEDULES_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_SCHEDULES_REGION_NAME", default="eu-west-2"),
)

event_bridge_client = Boto3HandlerSession.client("events")
event_bridge_scheduler = Boto3HandlerSession.client("scheduler", config=config)

logger = logging.getLogger(__name__)


def create_reminder(comment_id, date_time, pr_id, issue_id, message, user):
    target = {
        "Arn": os.environ.get("AWS_REMINDER_LAMBDA_ARN", ""),
        "RoleArn": os.environ.get("AWS_REMINDER_LAMBDA_ROLE_ARN", ""),
        "Input": json.dumps({"pr_id": pr_id, "issue_id": issue_id, "message": message, "user": user}),
    }
    logger.info(f"target: {target}")
    logger.info(f"schedule_expression: at({date_time})")
    logger.info(f"")
    return event_bridge_scheduler.create_schedule(
        Name=f"{str(uuid.uuid4())}",
        GroupName="myfinances-github-bot-remind_me",
        FlexibleTimeWindow={"Mode": "OFF"},
        ScheduleExpression=f"at({date_time})",
        Target=target,
        ActionAfterCompletion="DELETE",
    )
