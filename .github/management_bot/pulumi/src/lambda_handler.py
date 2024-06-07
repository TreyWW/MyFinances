import os, base64
from textwrap import dedent

import github.GithubException
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


def is_owner(issue, sender):
    return sender["id"] == issue["user"]["id"]


def is_trey(sender):
    return str(sender["id"]) == "171095439"


def lambda_handler(event: dict, _):
    auth = Auth.AppAuth(APP_ID, PRIVATE_KEY).get_installation_auth(event.get("installation", {}).get("id"))
    g = Github(auth=auth)

    ACTION = event.get("action", {})
    ISSUE = event.get("issue", {})
    PR = event.get("pull_request", {})
    COMMENT = event.get("comment", {})
    SENDER = event.get("sender", {})
    REPOSITORY = event.get("repository", {})

    repo = g.get_repo(event.get("repository", {}).get("full_name")) if REPOSITORY else {}

    if ISSUE or PR:
        selected_json: dict = ISSUE or PR

        selected_obj = repo.get_issue(number=ISSUE["number"]) if repo and ISSUE else repo.get_pull(number=PR["id"]) if repo and PR else {}

        LABELS = selected_json.get("labels")
        label_names = {label["name"] for label in LABELS}

        if "awaiting-response" in label_names and is_owner(selected_json, SENDER) and COMMENT:
            try:
                selected_obj.remove_from_labels("awaiting-response")
            except github.GithubException:
                ...

        if COMMENT and (is_trey(SENDER) or is_owner(selected_json, SENDER)):
            if ACTION == "created":  # sent comment
                msg = COMMENT.get("body", "")
                msg_stripped = msg.strip().split(" ")
                msg_len = len(msg_stripped)

                match msg_stripped[0]:
                    case "/add_label":
                        if not msg_len == 2:
                            send_error(
                                selected_obj,
                                sender=SENDER["login"],
                                body=COMMENT["body"],
                                msg_len=msg_len,
                                required=2,
                                example_cmd="add_label bug",
                            )

                            return g.close()

                        selected_obj.add_to_labels(msg_stripped[1])
                        selected_obj.create_comment(f"Okay @{SENDER['login']}, I have added the label '{msg_stripped[1]}'")
                    case "/add_labels":
                        selected_obj.add_to_labels(*msg_stripped[1:])
                        selected_obj.create_comment(f"Okay @{SENDER['login']}, I have added the labels \"{', '.join(msg_stripped[1:])}\"")
                    case "/remove_label":
                        if not msg_len == 2:
                            send_error(
                                selected_obj,
                                sender=SENDER["login"],
                                body=COMMENT["body"],
                                msg_len=msg_len,
                                required=2,
                                example_cmd="remove_label bug",
                            )

                            return g.close()

                        selected_obj.remove_from_labels(msg_stripped[1])
                        selected_obj.create_comment(f"Okay @{SENDER['login']}, I have removed the label \"{msg_stripped[1]}\"")
                    case "/remove_labels":
                        selected_obj.remove_from_labels(*msg_stripped[1:])
                        selected_obj.create_comment(f"Okay @{SENDER['login']}, I have removed the labels \"{', '.join(msg_stripped[1:])}\"")
                    case _:
                        selected_obj.create_comment(
                            dedent(
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
                        )
    # elif PR:
    #     match ACTION:
    #         case "labeled":
    #

    return {"statusCode": 200, "body": {}}
