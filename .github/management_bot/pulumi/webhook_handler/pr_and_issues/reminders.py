import os
import re
from textwrap import dedent
from datetime import datetime, timedelta

if os.environ.get("AWS_EXECUTION_ENV") is not None:
    import _types
    import helpers
    import boto3_handler
else:
    from .. import _types
    from .. import helpers
    from .. import boto3_handler


def parse_duration(duration) -> timedelta | None:
    pattern = re.compile(r"(\d+)([wdhm])")
    matches = pattern.match(duration)

    if not matches:
        return None

    value = int(matches.group(1))
    unit = matches.group(2)
    delta: timedelta

    if unit == "w":
        delta = timedelta(weeks=value)
    elif unit == "d":
        delta = timedelta(days=value)
    elif unit == "h":
        delta = timedelta(hours=value)
    elif unit == "m":
        delta = timedelta(minutes=value)
    else:
        return None

    return delta


def invalid_usage(context_objs) -> list[str]:
    context_objs.issue.create_comment(
        dedent(
            f"""
                Invalid usage. Example usage:
                - `/remind 2d`
                - `/remind 1w revamp this`

                {helpers.del_reply_comment()}
            """
        )
    )
    return ["added_issue_comment (invalid /remind args)"]


def validate_reminder_command(split, context_objs) -> datetime | list[str]:
    if len(split) < 2:
        return invalid_usage(context_objs)

    duration = parse_duration(split[1])
    if not duration:
        return invalid_usage(context_objs)

    print(f"duration: {duration}")
    print(f"now: {datetime.now()}")
    print(f"result: {datetime.now() + duration}")

    return datetime.now() + duration
