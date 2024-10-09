import json
import os, base64
import urllib.request
from textwrap import dedent

from github import Github, Issue, GithubIntegration, PullRequest
from github import Auth

import logging
import helpers

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG if os.environ.get("DEBUG") else logging.DEBUG)  # todo go back to info
logger = logging.getLogger(__name__)

aws_session_token = os.environ.get("AWS_SESSION_TOKEN")

REPOSITORY_NAME = "TreyWW/MyFinances"


def lambda_handler(event: dict, lambda_context):
    print(f"EVENT_DETAILS: {event}")
    # https://docs.aws.amazon.com/systems-manager/latest/userguide/ps-integration-lambda-extensions.html
    stage = "production"
    req = urllib.request.Request(
        f"http://localhost:2773/systemsmanager/parameters/get?withDecryption=true&name=%2Fmyfinances%2Fgithub_bot%2F{stage}"
    )
    req.add_header("X-Aws-Parameters-Secrets-Token", aws_session_token)
    config = urllib.request.urlopen(req).read()

    ssm_result: json = json.loads(config)
    ssm_value: json = json.loads(ssm_result["Parameter"]["Value"])

    PRIVATE_KEY = helpers.decode_private_key(ssm_value["private_key"])
    APP_ID = ssm_value["app_id"]

    auth = Auth.AppAuth(APP_ID, PRIVATE_KEY)
    gi = GithubIntegration(auth=auth)
    g: Github = gi.get_installations()[0].get_github_for_installation()

    repository = g.get_repo(REPOSITORY_NAME)

    target: Issue.Issue | PullRequest.PullRequest
    message: str = event.get("message")

    if issue_id := event.get("issue_id"):
        target = repository.get_issue(issue_id)
    elif pr_id := event.get("pr_id"):
        target = repository.get_pull(pr_id)
    else:
        raise ValueError("No issue or pull request specified")

    target.create_comment(
        dedent(
            f"""
                :wave: @{event.get("user")}, {message if message else "you set a reminder for now!"}

                {helpers.del_reply_comment()}
            """
        )
    )

    return {"statusCode": 200, "body": json.dumps({}), "headers": {"Content-Type": "application/json"}}
