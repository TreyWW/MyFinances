import json
import os, base64
import urllib.request
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

aws_session_token = os.environ.get("AWS_SESSION_TOKEN")

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


def lambda_handler(event: dict, lambda_context):
    # https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html
    stage = "staging" if lambda_context.function_version == "$LATEST" else "production"
    req = urllib.request.Request(
        f"http://localhost:2773/systemsmanager/parameters/get?withDecryption=true&name=%2Fmyfinances%2Fgithub_bot%2F{stage}"
    )
    req.add_header("X-Aws-Parameters-Secrets-Token", aws_session_token)
    config = urllib.request.urlopen(req).read()

    logger.info(f"Using stage: {stage}")

    ssm_result: json = json.loads(config)
    ssm_value: json = json.loads(ssm_result["Parameter"]["Value"])

    PRIVATE_KEY = decode_private_key(ssm_value["private_key"])
    APP_ID = ssm_value["app_id"]

    logger.info(f"Using app id: {APP_ID}")

    auth = Auth.AppAuth(APP_ID, PRIVATE_KEY)
    gi = GithubIntegration(auth=auth)
    g: Github = gi.get_installations()[0].get_github_for_installation()

    logger.debug(event)

    context_dicts = _types.Context(
        event=event,
        lambda_context=lambda_context,
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

    actions_taken = []

    if context_dicts.pull_request:
        logger.debug("Using PR handler")
        actions_taken.extend(pr_handler.handler(context_dicts, context_objs))
    elif context_dicts.issue:
        logger.debug("Using issue handler")
        actions_taken.extend(issue_handler.handler(context_dicts, context_objs))
    else:
        logger.debug("Using no handler; invalid request.")

    logger.info("Actions taken: %s", actions_taken)

    return {"statusCode": 200, "body": json.dumps({"actions_taken": actions_taken}), "headers": {"Content-Type": "application/json"}}
