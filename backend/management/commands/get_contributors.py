import json
import os

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Adds contributors HTML table to README.md file.
    """

    def handle(self, *args, **kwargs):
        # Get the path to the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to contributors.json file in the same directory as the script
        contributors_json_path = os.path.join(script_dir, "contributors.json")
        readme_path = "README.md"

        try:
            # Load JSON data from contributors.json file
            with open(contributors_json_path, "r", encoding="utf-8") as json_file:
                contributors_json = json_file.read()
                contributors_data = json.loads(contributors_json)
        except FileNotFoundError:
            self.stderr.write(
                self.style.ERROR(
                    "contributors.json file not found. Please make sure the file exists."
                )
            )
            return
        except json.JSONDecodeError:
            self.stderr.write(
                self.style.ERROR(
                    "Error decoding JSON data from contributors.json file. Please check the file contents."
                )
            )
            return

        # HTML template for each contributor entry
        contributor_template = """
        <td align="center">
            <a href="https://github.com/{username}">
                <img src="https://github.com/{username}.png" width="100px;" alt="" />
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
                            "🧪",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Added Tests",
                        ),
                        (
                            "🐳",
                            f'https://github.com/TreyWW/MyFinances/pulls?q=is%3Apr+author%3A{contributor["username"]}',
                            "Docker",
                        ),
                    ]
                    if tag_icon in contributor.get("tags", [])
                ]
            )
            return contributor_template.format(
                username=contributor["username"],
                name=contributor["name"],
                tags=tags_html,
            )

        # Generate HTML for contributors
        contributors_html = ""
        users_per_row = 6
        for index, contributor in enumerate(contributors_data, start=1):
            if (index - 1) % users_per_row == 0 and index > 1:
                contributors_html += "</tr><tr>"
            contributors_html += f"<td>{generate_contributor_html(contributor)}</td>"

        # Wrap the entire content in a table row
        contributors_html = f"<tr>{contributors_html}</tr>"

        try:
            # Read the README.md file
            with open(readme_path, "r", encoding="utf-8") as readme_file:
                readme_content = readme_file.read()
        except FileNotFoundError:
            self.stderr.write(
                self.style.ERROR(
                    "README.md file not found. Please make sure the file exists."
                )
            )
            return

        # Insert the generated HTML between the comments
        start_comment = "<!-- CONTRIBUTORS TABLE START -->"
        end_comment = "<!-- CONTRIBUTORS TABLE END -->"
        start_index = readme_content.find(start_comment) + len(start_comment)
        end_index = readme_content.find(end_comment)

        new_readme_content = (
            readme_content[:start_index]
            + "\n<table>\n"
            + contributors_html
            + "</table>\n"
            + readme_content[end_index:]
        )

        # Write the modified content back to the README.md file
        with open(readme_path, "w", encoding="utf-8") as readme_file:
            readme_file.write(new_readme_content)

        self.stdout.write(
            self.style.SUCCESS("HTML table inserted into README.md successfully.")
        )
