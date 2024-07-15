import os
import re
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
    if not re.match(r"^(bug|idea|implement|cleanup):\s*\S.*", context_objs.issue.title) and context_objs.sender.type == "User":
        logger.info(f"Regex title doesn't match. {context_objs.issue.title} doesnt start with bug|idea|implement|cleanup:")
        logger.info(f"Commenting on {context_objs.issue.html_url}")
        context_objs.issue.create_comment(
            dedent(
                f"""
                    Hi @{context_objs.sender.login},

                    You have chosen a title that is slightly different to our title standards. Please, if possible, use the format:
                    (bug, idea, implement or cleanup) : Title

                    e.g. "bug: xyz page doesn't work"

                    {helpers.del_reply_comment()}
            """
            )
        )
        return ["added_issue_comment (invalid title)"]
    return []


def delete_reply_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    match = re.search(r"DELREPLY-(.{8})", context_dicts.comment.body)

    if not match or context_objs.sender.type != "User":
        return []

    logger.info("Deleting comment due to DELREPLY in body")

    reference_code = match.group(1)

    logger.debug(f"Deleting comment with reference code: {reference_code}")

    for comment in context_objs.issue.get_comments():
        if f"DELREPLY-{reference_code}" in comment.body.upper():
            # comment.delete()  # delete users reply comment
            context_objs.issue.get_comment(context_dicts.comment.id).delete()  # delete bots comment
            return ["deleted_issue_comment (DEL REPLY)"]


def command_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> list[str]:
    base_message = context_dicts.comment.body
    split = base_message.split()
    command = split[0]

    logger.info(f"Extracted Command: {command}")

    if command == "/project_info":
        context_objs.issue.create_comment(
            dedent(
                f"""
                You can view our documentation at\
                [docs.myfinances.cloud](https://docs.myfinances.cloud/?utm_source=issue_{context_objs.issue.number}).

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
                responses.extend(delete_reply_handler(context_dicts, context_objs))
                responses.extend(command_handler(context_dicts, context_objs))
    return responses
