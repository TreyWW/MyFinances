from __future__ import annotations

import logging
import boto3
from botocore.config import Config
from settings.helpers import get_var
from settings.settings import AWS_TAGS_APP_NAME

config = Config(connect_timeout=5, retries={"max_attempts": 2})

DEBUG_LEVEL = get_var("AWS_PRINT_DEBUG_LEVEL", default="info")
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
