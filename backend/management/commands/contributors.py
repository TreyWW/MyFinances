import json
import os
from typing import TypedDict

from django.core.management.base import BaseCommand
from django.utils.termcolors import colorize


class ContributorsItem(TypedDict):
    name: str
    username: str
    role: str
    tags: list[str]


class Command(BaseCommand):
    """
    Adds contributors HTML table to README.md file.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.contributors_json_path = os.path.join(self.script_dir, "contributors.json")
        self.readme_path = "README.md"

    def add_arguments(self, parser):
        parser.add_argument("action", type=str, help="sync, list, add, edit")

        parser.add_argument("--sort", type=str, help="Sort by: name, username or role")
        parser.add_argument("--limit", type=int, default=20, help="Limit results by amount")

        parser.add_argument("name", type=str, nargs="?", help="users human/readable name")
        parser.add_argument("--name", type=str, help="users human/readable name")
        parser.add_argument("username", type=str, nargs="?", help="github username")
        parser.add_argument("--username", type=str, help="github username")
        parser.add_argument("role", type=str, nargs="?", help="role in team")
        parser.add_argument("--role", type=str, help="role in team")
        parser.add_argument("tags", type=str, nargs="*", help="comma separated list of tags")
        parser.add_argument("--tags", type=str, help="comma separated list of tags")

    def handle(self, *args, **kwargs):
        action = kwargs["action"]

        if action == "sync":
            self.sync_contributors()
        elif action == "list":
            self.list_contributors(*args, **kwargs)
        elif action == "add":
            self.add_contributor(*args, **kwargs)
        elif action == "help":
            self.stdout.write(
                colorize(
                    """
Please provide valid action.
- sync
- list --sort <name|username|role> --limit <int>
- add <name> <username> <role> <tags>
    to use multi-word usernames or names, surround with quotes
    tags can be space separated
    to change the order use --, e.g. --name bob
            """,
                    fg="red",
                    opts=("bold",),
                )
            )
        else:
            self.stdout.write(colorize("Please provide valid action. \n - sync \n - list \n - add \n - help", fg="red", opts=("bold",)))

    def add_contributor(self, *args, **kwargs):
        name: str = kwargs.get("name")
        username: str = kwargs.get("username")
        role: str = kwargs.get("role")
        tags: list[str] = kwargs.get("tags")

        if not name or not username or not role or not tags:
            return self.stdout.write(colorize("Please provide name, username, role and tags", fg="red", opts=("bold",)))

        if not all([t in ["👑", "🖥", "🎨", "📖", "🐳", "♻", "🐞"] for t in tags]):
            return self.stdout.write(
                colorize(f"Please provide valid tags. Valid tags are: 👑, 🖥, 🎨, 📖, 🐳, ♻, 🐞", fg="red", opts=("bold",))
            )

        contributors_data: list[ContributorsItem] = self._read_contributor_file()

        for user in contributors_data:
            if user["username"] == username:
                return self.stdout.write(colorize("User already exists", fg="red", opts=("bold",)))

        contributor_obj = ContributorsItem(name=name, username=username, role=role, tags=tags)

        if contributors_data:
            contributors_data.append(contributor_obj)
        else:
            return self.stdout.write(
                colorize("contributors.json file not found. Please make sure the file exists.", fg="red", opts=("bold",))
            )

        self._save_contributors_file(contributors_data)

    def list_contributors(self, *args, **kwargs):
        contributors_data: list[ContributorsItem] | None = self._read_contributor_file()

        if not contributors_data:
            return

        if kwargs.get("sort") == "name":
            contributors_data = sorted(contributors_data, key=lambda d: d.get("name", ""))
        elif kwargs.get("sort") == "username":
            contributors_data = sorted(contributors_data, key=lambda d: d.get("username", ""))
        elif kwargs.get("sort") == "role":
            contributors_data = sorted(contributors_data, key=lambda d: d.get("role", ""))

        if limit := kwargs.get("limit"):
            bef_count = len(contributors_data)
            contributors_data = contributors_data[:limit]
            aft_count = len(contributors_data)

        max_w_name = max(len(d.get("name", "")) + 4 for d in contributors_data)
        max_w_username = max(len(d.get("username", "")) + 4 for d in contributors_data)
        max_w_role = max(len(d.get("role", "")) + 4 for d in contributors_data)

        row_str = "{:<{max_w_name}} {:<{max_w_username}} {:<{max_w_role}} {:<10}"

        header = row_str.format(
            "Name", "Username", "Role", "Tags", max_w_name=max_w_name, max_w_username=max_w_username, max_w_role=max_w_role
        )

        self.stdout.write(header)

        for user in contributors_data:
            row = row_str.format(
                user.get("name"),
                user.get("username"),
                user.get("role"),
                " ".join(user.get("tags")),
                max_w_name=max_w_name,
                max_w_username=max_w_username,
                max_w_role=max_w_role,
            )
            self.stdout.write(row)

        if limit:
            # noinspection PyUnboundLocalVariable
            self.stdout.write(f"\nShowing {aft_count} of {bef_count} contributors\n")

    def sync_contributors(self):
        contributors_data = self._read_contributor_file()

        if not contributors_data:
            return

        # Path to contributors.json file in the same directory as the script

        # HTML template for each contributor entry
        contributor_template = """
                <td align="center">
                    <a href="https://github.com/{username}" title="{username}">
                        <img title="{role}" src="https://github.com/{username}.png" width="100px;" alt="" />
                        <br />
                        <sub>
                            <b>{name}</b>
                        </sub>
                    </a>
                    <br />
                    {tags}
                </td>
                """

        # Function to generate HTML for a contributor
        def generate_contributor_html(contributor):
            tags_html = "".join(
                [
                    f'<a href="{tag_link}" title="{tag_title}">{tag_icon}</a>'
                    for tag_icon, tag_link, tag_title in [
                        (
                            "👑",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=user%3A{contributor["username"]}',
                            "Project Lead",
                        ),
                        (
                            "🖥",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Backend",
                        ),
                        (
                            "📖",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Documentation",
                        ),
                        (
                            "🎨",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Frontend",
                        ),
                        (
                            "🐞",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Bug Fixes",
                        ),
                        (
                            "🧪",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Added Tests",
                        ),
                        (
                            "🐳",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Docker",
                        ),
                        (
                            "♻",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Refactored Files",
                        ),
                    ]
                    if tag_icon in contributor.get("tags", [])
                ]
            )
            return contributor_template.format(
                username=contributor["username"],
                name=contributor["name"],
                role=contributor.get("role"),
                tags=tags_html,
            )

        # Generate HTML for contributors
        contributors_html = ""
        users_per_row = 5
        for index, contributor in enumerate(contributors_data, start=1):
            if (index - 1) % users_per_row == 0 and index > 1:
                contributors_html += "</tr><tr>"
            contributors_html += f"<td>{generate_contributor_html(contributor)}</td>"

        # Wrap the entire content in a table row
        contributors_html = f"<tr>{contributors_html}</tr>"

        try:
            # Read the README.md file
            with open(self.readme_path, encoding="utf-8") as readme_file:
                readme_content = readme_file.read()
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("README.md file not found. Please make sure the file exists."))
            return

        # Insert the generated HTML between the comments
        start_comment = "<!-- CONTRIBUTORS TABLE START -->"
        end_comment = "<!-- CONTRIBUTORS TABLE END -->"
        start_index = readme_content.find(start_comment) + len(start_comment)
        end_index = readme_content.find(end_comment)

        new_readme_content = readme_content[:start_index] + "\n<table>\n" + contributors_html + "</table>\n" + readme_content[end_index:]

        self._save_readme_file(new_readme_content)

        self.stdout.write(self.style.SUCCESS("HTML table inserted into README.md successfully."))

    def _read_contributor_file(self) -> list[ContributorsItem] | None:
        try:
            # Load JSON data from contributors.json file
            with open(self.contributors_json_path, encoding="utf-8") as json_file:
                contributors_json = json_file.read()
                return json.loads(contributors_json)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("contributors.json file not found. Please make sure the file exists."))
            return None
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR("Error decoding JSON data from contributors.json file. Please check the file contents."))
            return None

    def _read_readme_file(self) -> str | None:
        try:
            # Read the README.md file
            with open(self.readme_path, encoding="utf-8") as readme_file:
                return readme_file.read()
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("README.md file not found. Please make sure the file exists."))
            return None

    def _save_contributors_file(self, contributors_data: list[ContributorsItem]):
        try:
            # Save JSON data to contributors.json file
            with open(self.contributors_json_path, "w", encoding="utf-8") as json_file:
                json.dump(contributors_data, json_file, indent=4, ensure_ascii=False)
        except FileNotFoundError:
            self.stderr.write(self.style.ERROR("contributors.json file not found. Please make sure the file exists."))
            return
        except json.JSONDecodeError:
            self.stderr.write(self.style.ERROR("Error encoding JSON data to contributors.json file. Please check the file contents."))
            return

    def _save_readme_file(self, new_readme_content):
        with open(self.readme_path, "w", encoding="utf-8") as readme_file:
            readme_file.write(new_readme_content)
