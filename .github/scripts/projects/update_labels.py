import os
import requests
import json


def get_issue_number(issue_url, headers):
    response = requests.get(issue_url, headers=headers)
    response.raise_for_status()
    issue_data = response.json()
    return issue_data["number"]


def update_labels(issue_number, add_labels: list[str], remove_labels: list[str], repo_owner, repo_name, headers):
    # Add new label
    requests.post(
        f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/labels", json={"labels": add_labels}, headers=headers
    ).raise_for_status()

    # Remove old labels
    for label in remove_labels:
        requests.delete(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues/{issue_number}/labels/{label}", headers=headers
        ).raise_for_status()


def main():
    column_id_to_label_map = {
        "Suggested": {"add": ["idea: deciding", "idea"], "remove": ["idea: suggested"]},
        "Deciding": {"add": ["idea: suggested", "idea"], "remove": ["idea: accepted", "idea: suggested"]},
    }

    github_token = os.getenv("GITHUB_TOKEN")
    github_repository = os.getenv("GITHUB_REPOSITORY")
    github_event_path = os.getenv("GITHUB_EVENT_PATH")

    with open(github_event_path, "r") as f:
        event_data = json.load(f)
    project_id = str(event_data["project_card"]["project_id"])

    if project_id != "18":
        print("Skipping project card because it isn't in the IDEAS board.")
        return

    column_id = str(event_data["project_card"]["column_id"])
    issue_url = event_data["project_card"]["content_url"]
    repo_owner, repo_name = github_repository.split("/")

    if column_id in column_id_to_label_map:
        issue_number = get_issue_number(issue_url, headers={"Authorization": f"token {github_token}"})
        labels = column_id_to_label_map[column_id]
        update_labels(
            issue_number, labels["add"], labels["remove"], repo_owner, repo_name, headers={"Authorization": f"token {github_token}"}
        )


if __name__ == "__main__":
    main()
