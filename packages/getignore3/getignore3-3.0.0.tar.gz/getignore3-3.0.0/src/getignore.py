"""
Get gitignore files without bothering yourself
"""

import argparse
import os
import sys

import requests


argparser = argparse.ArgumentParser(
    prog="getignore",
    description="Get gitignore files without bothering yourself",
)

argparser.add_argument(
    "template_name",
    nargs="*",
    help="Name(s) of gitignore templates to fetch (e.g., Python, Node and etc.)",
)
argparser.add_argument(
    "-l",
    "--list-templates",
    action="store_true",
    help="List available gitignore templates",
)
argparser.add_argument(
    "-o",
    "--override",
    action="store_true",
    help="Override existing gitignore file instead of appending",
)


def getignore() -> None:
    """
    Get gitignore files without bothering yourself
    """

    args = argparser.parse_args()

    if args.list_templates:
        repository_contents = requests.get(
            "https://api.github.com/repos/github/gitignore/contents/"
        ).json()
        available_templates = [
            item["name"]
            for item in repository_contents
            if item["name"].endswith(".gitignore")
        ]

        print("Available gitignore templates:")
        print(", ".join(available_templates))
        return

    template_names = args.template_name

    content_to_write = ""

    if template_names is None:
        print("Nothing happened!")
        return

    for name in template_names:
        getignore_request = requests.get(
            f"https://raw.githubusercontent.com/github/gitignore/main/{name}.gitignore"
        )

        if getignore_request.status_code >= 400:
            print(
                f"Error {getignore_request.status_code}, Couldn't get the gitignore template!",
                file=sys.stderr,
            )
            return

        print(f"Got the {name!r} gitignore template!")
        content_to_write += getignore_request.text + "\n"

    didnt_gitignore_exist = not os.path.exists(".gitignore")

    with open(".gitignore", "w" if args.override else "a") as gitignore:
        gitignore.write(content_to_write)

    if didnt_gitignore_exist:
        print("Created the gitignore file!")

    elif args.override:
        print("Overwrote the gitignore file!")

    else:
        print("Appended new things to the gitignore file!")


if __name__ == "__main__":
    getignore()
