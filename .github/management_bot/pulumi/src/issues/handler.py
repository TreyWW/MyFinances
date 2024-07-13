import os
import re
from textwrap import dedent
import logging
import secrets

import github.Issue

from re import match

import string

import random

logger = logging.getLogger(__name__)
if os.environ.get("AWS_EXECUTION_ENV") is not None:
    import _types
else:
    from .. import _types


def title_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> None:
    if not re.match(r"^(bug|idea|implement|cleanup):\s*\S.*", context_objs.issue.title):
        logger.info(f"Regex title doesn't match. {context_objs.issue.title} doesnt start with bug|idea|implement|cleanup:")
        logger.info(f"Commenting on {context_objs.issue.html_url}")
        context_objs.issue.create_comment(
            dedent(
                f"""
                    Hi @{context_objs.sender.login},

                    You have chosen a title that is slightly different to our title standards. Please, if possible, use the format:
                    (bug, idea, implement or cleanup) : Title

                    e.g. "bug: xyz page doesn't work"

                    > If you would like to ignore this message, please reply with the reference `DELREPLY-
                    {''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}` (you may delete this reply afterwards)
            """
            )
        )


def delete_reply_handler(context_dicts: _types.Context, context_objs: _types.Objects) -> None:
    match = re.search(r"DELREPLY-(.{8})", context_dicts.comment.body)

    if not match:
        return

    logger.info("Deleting comment due to DELREPLY in body")

    reference_code = match.group(1)

    logger.debug(f"Deleting comment with reference code: {reference_code}")

    context_objs.issue: github.Issue.Issue

    for comment in context_objs.issue.get_comments():
        if f"DELREPLY-{reference_code}" in comment.body.upper():
            # comment.delete()  # delete users reply comment
            context_objs.issue.get_comment(context_dicts.comment.id).delete()  # delete bots comment
            break


def handler(context_dicts: _types.Context, context_objs: _types.Objects) -> None:
    logger.info(f"action: {context_dicts.action}")
    match context_dicts.action:
        case "opened":
            logger.info("Using title handler due to opened issue")
            title_handler(context_dicts, context_objs)
        case "edited":
            if context_dicts.changes.title and context_dicts.changes.title["from"]:
                title_handler(context_dicts, context_objs)
        case "created":
            if context_dicts.comment:
                delete_reply_handler(context_dicts, context_objs)
