import json, os, base64

from github import Github, Issue
from github import Auth

raw_private_key = os.environ.get("private_key")
PRIVATE_KEY = base64.b64decode(raw_private_key).decode("ascii")
APP_ID = os.environ.get("app_id")


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


def lambda_handler(event, context):
    auth = Auth.AppAuth(APP_ID, PRIVATE_KEY).get_installation_auth(event.get("installation", {}).get("id"))
    g = Github(auth=auth)

    ACTION = event.get("action", {})
    ISSUE = event.get("issue", {})
    COMMENT = event.get("comment", {})
    SENDER = event.get("sender", {})
    REPOSITORY = event.get("repository", {})

    repo = g.get_repo(event.get("repository", {}).get("full_name"))

    if ISSUE and COMMENT and str(SENDER.get("id")) != "171095439":
        if ACTION == "created":  # sent comment
            issue = repo.get_issue(number=ISSUE.get("number"))
            msg = COMMENT.get("body", "")
            msg_stripped = msg.strip().split(" ")
            msg_len = len(msg_stripped)

            if msg_stripped[0] == "/add_label":
                if not msg_len == 2:
                    send_error(
                        issue, sender=SENDER["login"], body=COMMENT["body"], msg_len=msg_len, required=2, example_cmd="add_label bug"
                    )

                    return g.close()

                issue.add_to_labels(msg_stripped[1])
                issue.create_comment(f"Okay @{SENDER['login']}, I have added the label '{msg_stripped[1]}'")
            elif msg_stripped[0] == "/add_labels":
                issue.add_to_labels(*msg_stripped[1:])
                issue.create_comment(f"Okay @{SENDER['login']}, I have added the labels \"{', '.join(msg_stripped[1:])}\"")
            elif msg_stripped[0] == "/remove_label":
                if not msg_len == 2:
                    send_error(
                        issue, sender=SENDER["login"], body=COMMENT["body"], msg_len=msg_len, required=2, example_cmd="remove_label bug"
                    )

                    return g.close()

                issue.remove_from_labels(msg_stripped[1])
                issue.create_comment(f"Okay @{SENDER['login']}, I have removed the label \"{msg_stripped[1]}\"")
            elif msg_stripped[0] == "/remove_labels":
                issue.remove_from_labels(*msg_stripped[1:])
                issue.create_comment(f"Okay @{SENDER['login']}, I have removed the labels \"{', '.join(msg_stripped[1:])}\"")
            elif msg_stripped[0] == "/help":
                issue.create_comment(
                    f"""
Hi @{SENDER["login"]},

<details><summary>My available commands:</summary>
<p>

| Command | Description | Arg Types | Example |
|---------|-------------|--------|--------|
| /add_label | Adds one label | string | /add_label bug |
| /add_labels | Adds multiple labels | list[string] | /add_label bug enhancement |
| /remove_label | Removes one label | string | /remove_label bug |
| /remove_labels | Removes multiple labels | list[string] | /remove_labels bug enhancement |
</p>
</details>
"""
                )

    return {"statusCode": 200, "body": json.dumps("Success")}
