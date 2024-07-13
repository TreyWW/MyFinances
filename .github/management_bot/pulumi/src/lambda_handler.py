import json
import os, base64
from textwrap import dedent

import github.GithubException
from prs import handler as pr_handler
from issues import handler as issue_handler
from helpers import decode_private_key
import _types
from github import Github, Issue, GithubIntegration
from github import Auth

import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG if os.environ.get("DEBUG") else logging.DEBUG)  # todo go back to info
logger = logging.getLogger(__name__)

PRIVATE_KEY = decode_private_key(os.environ.get("private_key"))
APP_ID = os.environ.get("app_id")

REPOSITORY_NAME = "TreyWW/MyFinances"


def check_if_user_perm_issue(issue: dict, sender: dict, repository: dict):
    return issue.get("user", {}).get("id") == sender.get("id") or sender.get("id") == repository.get("owner", {}).get("id")


TEMPLATE_ERROR_MESSAGE = """
    {body}
_Replying to @{sender}_

Invalid command, you inserted {msg_len} out of the {required} required parameters.

<details><summary>Additional Details</summary>
<p>

> Example: `/{example_cmd}`

> You may use `/help` for more commands.
</p>
</details>"""


def send_error(issue, *, body, sender, msg_len, required, example_cmd):
    return issue.create_comment(
        TEMPLATE_ERROR_MESSAGE.format(sender=sender, body=body, msg_len=msg_len, required=required, example_cmd=example_cmd)
    )


def is_owner(issue, sender):
    return sender["id"] == issue["user"]["id"]


def is_trey(sender):
    return str(sender["id"]) == "171095439"


def lambda_handler(event: dict, _):
    auth = Auth.AppAuth(APP_ID, PRIVATE_KEY)
    gi = GithubIntegration(auth=auth)
    g: Github = gi.get_installations()[0].get_github_for_installation()

    logger.debug(event)

    context_dicts = _types.Context(
        event=event,
        action=event.get("action", ""),
        issue=_types.fill_dataclass_from_dict(_types.Issue, event.get("issue", {})),
        pull_request=_types.fill_dataclass_from_dict(_types.PullRequest, event.get("pull_request", {})),
        comment=_types.fill_dataclass_from_dict(_types.Comment, event.get("comment", {})),
        sender=_types.fill_dataclass_from_dict(_types.User, event.get("sender", {})),
        repository=_types.fill_dataclass_from_dict(_types.Repository, event.get("repository", {})),
        changes=_types.fill_dataclass_from_dict(_types.Changes, event.get("changes", {})),
    )

    logger.debug(context_dicts)

    context_objs = _types.Objects(github=g, dict_context=context_dicts, repository=g.get_repo(context_dicts.repository.full_name))

    logger.debug(context_objs)

    if context_dicts.pull_request:
        logger.debug("Using PR handler")
        pr_handler.handler(context_dicts, context_objs)
    elif context_dicts.issue:
        logger.debug("Using issue handler")
        issue_handler.handler(context_dicts, context_objs)
    else:
        logger.debug("Using no handler; invalid request.")

    return {"statusCode": 200, "body": json.dumps({})}
