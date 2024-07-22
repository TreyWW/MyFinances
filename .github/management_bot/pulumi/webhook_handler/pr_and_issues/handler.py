import os
import re
from textwrap import dedent
import logging

logger = logging.getLogger(__name__)
if os.environ.get("AWS_EXECUTION_ENV") is not None:
    import _types
    import helpers
    from .reminders import validate_reminder_command
    import boto3_handler
else:
    from .. import _types
    from .. import helpers
    from ..pr_and_issues.reminders import validate_reminder_command
    from .. import boto3_handler


def delete_reply_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    match = re.search(r"DELREPLY-(.{8})", context_dicts.comment.body)

    if not match or context_objs.sender.type != "User":
        return []

    logger.info("Deleting comment due to DELREPLY in body")

    reference_code = match.group(1)

    logger.debug(f"Deleting comment with reference code: {reference_code}")

    for comment in context_objs.target_discussion.get_comments():
        if f"DELREPLY-{reference_code}" in comment.body.upper():
            comment.delete()  # delete users reply comment
            # context_objs.target_discussion.get_comment(context_dicts.comment.id).delete()  # delete bots comment
            return ["deleted_issue_comment (DEL REPLY)"]


def command_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    base_message = context_dicts.comment.body
    split = base_message.split()
    command = split[0]

    logger.info(f"Extracted Command: {command}")

    match command:
        # <editor-fold desc="/project_info">
        case "/project_info":
            context_objs.target_discussion.create_comment(
                dedent(
                    f"""
                    You can view our documentation at\
                    [docs.myfinances.cloud](https://docs.myfinances.cloud/\
                    ?utm_source={context_objs.target_discussion_type}_{context_objs.target_discussion.number}).

                    There you can find info such as:
                    - setting up guides
                    - code styles
                    - changelogs
                    - our discord server
                    - (soon) user usage guide

                    {f"> Mentioning @{split[1]}" if len(split) > 1 else ""}

                    {helpers.del_reply_comment()}
                    """
                )
            )
            return ["added_issue_comment (project info)"]
        # </editor-fold>
        # <editor-fold desc="/remind">
        case "/remind":
            logger.info("Using /remind")
            if len(split) < 2:
                logger.info("Invalid usage")
                context_objs.target_discussion.create_comment(
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

            duration: str = split[1]
            message: str = " ".join(split[2:]) if len(split) > 2 else ""

            datetime_or_error = validate_reminder_command(split, context_objs)

            logger.info(f"datetime_or_error: {datetime_or_error}")

            if isinstance(datetime_or_error, list):
                return datetime_or_error

            resp = boto3_handler.create_reminder(
                comment_id=context_objs,
                date_time=datetime_or_error.strftime("%Y-%m-%dT%H:%M:%S"),
                pr_id=None,
                issue_id=context_objs.target_discussion.number,
                message=message,
                user=context_objs.sender.login,
            )
            logger.info(f"resp: {resp}")

            context_objs.target_discussion.create_comment(
                dedent(
                    f"""
                        @{context_objs.sender.login}, ok! I will remind you {datetime_or_error.strftime("on %A, %B %-m, %y at %-H:%M %p")}!

                        {helpers.del_reply_comment()}
                    """
                )
            )
            return ["added_issue_comment (reminder success)"]
        case _:
            logger.info("No issue command")
            return []
        # </editor-fold>


def handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    logger.info(f"action: {context_dicts.action}")
    responses = []
    match context_dicts.action:
        case "opened":
            ...
        case "edited":
            ...
        case "created":
            if context_dicts.comment:
                responses.extend(delete_reply_handler(context_dicts, context_objs))
                responses.extend(command_handler(context_dicts, context_objs))
    return responses
