import os
import re
from datetime import datetime
from textwrap import dedent
import logging
import github.Issue

import string

import random

logger = logging.getLogger(__name__)
if os.environ.get("AWS_EXECUTION_ENV") is not None:
    import _types
    import helpers
else:
    from .. import _types
    from .. import helpers


def title_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    if not re.match(r"^(bug|idea|implement|cleanup|progress):\s*\S.*", context_objs.issue.title) and context_objs.sender.type == "User":
        logger.info(f"Regex title doesn't match. {context_objs.issue.title} doesnt start with bug|idea|implement|cleanup|progress:")
        logger.info(f"Commenting on {context_objs.issue.html_url}")
        context_objs.issue.create_comment(
            dedent(
                f"""
                    Hi @{context_objs.sender.login},

                    You have chosen a title that is slightly different to our title standards. Please, if possible, use the format:
                    (progress, bug, idea, implement or cleanup) : Title

                    e.g. "bug: xyz page doesn't work"

                    {helpers.del_reply_comment()}
            """
            )
        )
        return ["added_issue_comment (invalid title)"]
    return []


def command_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    base_message = context_dicts.comment.body
    split = base_message.split()
    command = split[0]

    logger.info(f"Extracted Command: {command}")

    # match command:
    # # <editor-fold desc="/project_info">
    # case "/project_info":
    #     context_objs.issue.create_comment(
    #         dedent(
    #             f"""
    #             You can view our documentation at\
    #             [docs.myfinances.cloud](https://docs.myfinances.cloud/?utm_source=issue_{context_objs.issue.number}).
    #
    #             There you can find info such as:
    #             - setting up guides
    #             - code styles
    #             - changelogs
    #             - our discord server
    #             - (soon) user usage guide
    #
    #             {f"> Mentioning @{split[1]}" if len(split) > 1 else ""}
    #
    #             {helpers.del_reply_comment()}
    #             """
    #         )
    #     )
    #     return ["added_issue_comment (project info)"]
    # # </editor-fold>
    # # <editor-fold desc="/remind">
    # case "/remind":
    #     logger.info("Using /remind")
    #     if len(split) < 2:
    #         logger.info("Invalid usage")
    #         context_objs.issue.create_comment(
    #             dedent(
    #                 f"""
    #                     Invalid usage. Example usage:
    #                     - `/remind 2d`
    #                     - `/remind 1w revamp this`
    #
    #                     {helpers.del_reply_comment()}
    #                     """
    #             )
    #         )
    #         return ["added_issue_comment (invalid /remind args)"]
    #
    #     duration: str = split[1]
    #     message: str = " ".join(split[2:]) if len(split) > 2 else ""
    #
    #     datetime_or_error = validate_reminder_command(split, context_objs)
    #
    #     logger.info(f"datetime_or_error: {datetime_or_error}")
    #
    #     if isinstance(datetime_or_error, list):
    #         return datetime_or_error
    #
    #     resp = boto3_handler.create_reminder(
    #         comment_id=context_objs,
    #         date_time=datetime_or_error.strftime("%Y-%m-%dT%H:%M:%S"),
    #         pr_id=None,
    #         issue_id=context_objs.issue.number,
    #         message=message,
    #         user=context_objs.sender.login,
    #     )
    #     logger.info(f"resp: {resp}")
    #
    #     context_objs.issue.create_comment(
    #         dedent(
    #             f"""
    #                 @{context_objs.sender.login}, ok! I will remind you {datetime_or_error.strftime("on %A, %B %-m, %y at %-H:%M %p")}!
    #
    #                 {helpers.del_reply_comment()}
    #             """
    #         )
    #     )
    #     return ["added_issue_comment (reminder success)"]
    # case _:
    #     logger.info("No issue command")
    #     return []
    # # </editor-fold>

    return []


def handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    logger.info(f"action: {context_dicts.action}")
    responses = []
    match context_dicts.action:
        case "opened":
            logger.info("Using title handler due to opened issue")
            responses.extend(title_handler(context_dicts, context_objs))
        case "edited":
            if context_dicts.changes.title and context_dicts.changes.title["from"]:
                responses.extend(title_handler(context_dicts, context_objs))
        case "created":
            if context_dicts.comment:
                responses.extend(command_handler(context_dicts, context_objs))
    return responses
