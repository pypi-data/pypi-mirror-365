# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "requests",
#     "nbformat",
# ]
# ///

import argparse
import re
import sys
from pathlib import Path

import nbformat
import requests


def build_pattern(excluded_words: list[str] | None):
    excluded_pattern = "|".join(re.escape(word) for word in excluded_words)
    return rf'(["\'])(?!(?:{excluded_pattern})\b)([A-Z]{{2,}}(?:\s+[A-Z]{{2,}})*)\1'


def get_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)


def get_text_from_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def detect_pii_in_repo(
    repo_path: str | Path,
    excluded_words: list[str],
    file_ext: None | str = None,
    verbose=bool | None,
):
    repo_path = Path(repo_path).expanduser()
    file_ext = file_ext or "ipynb"
    if file_ext == "ipynb":
        for file in repo_path.rglob("*.ipynb"):
            if verbose:
                print(f"Processing: {file}")
            with open(file, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
            text = "\n".join(
                cell["source"]
                for cell in nb.cells
                if cell.cell_type == "code" or cell.cell_type == "markdown"
            )
            detect_pii_by_regex(text, excluded_words, filename=file)
    else:
        for file in repo_path.rglob(f"*.{file_ext}"):
            if verbose:
                print(f"Processing: {file}")
            text = get_text_from_file(file)
            detect_pii_by_regex(text, excluded_words, filename=file)


def detect_pii_by_regex(
    text: str,
    excluded_words: list[str],
    filename: Path | str | None = None,
    verbose: bool | None = None,
):
    pattern = build_pattern(excluded_words)
    matches = re.findall(pattern, text)
    names = [match[1] for match in matches]
    if names:
        if filename:
            print(filename)
        print("Suspected names / initials found:")
        for name in names:
            print(f"- {name}")
    else:
        if verbose:
            print("No matching names/initials found.")


def main():
    repo_path = None
    text = None

    parser = argparse.ArgumentParser(description="Scan for ALL CAPS names in quotes.")
    parser.add_argument("--url", help="URL of the file to scan")
    parser.add_argument("--file", help="Path to a local file to scan")
    parser.add_argument("--repo", help="Path to a local repo")
    parser.add_argument(
        "--exclude",
        nargs="+",
        default=[],
        help="List of extra ALL CAPS words to exclude from matches",
    )
    parser.add_argument("--ext", default="ipynb", help="file extension")
    parser.add_argument("--verbose", default=False, help="verbose output")
    # parser.add_argument("--regex", default=None, help="override default regex")
    # parser.add_argument("--add-regex", dest="add_regex",
    # default=None, help="add a regex to the default regex")

    args = parser.parse_args()

    if args.url:
        print(args.url)
        text = get_text_from_url(args.url)
    elif args.file:
        print(args.file)
        text = get_text_from_file(args.file)
    elif args.repo:
        print(args.repo)
        if not Path(args.repo).exists():
            print(f"No such repo: {args.repo}")
        repo_path = Path(args.repo)
    else:
        print("Please provide either --url or --file or --repo.")
        sys.exit(1)

    excluded_words = [
        "LICENSE",
        "TERMS",
        "CONFIDENTIAL",
        "FALSE",
        "TRUE",
        "KEYED",
        "COMPLETE",
        "INCOMPLETE",
        "IN_PROGRESS",
        "NEW",
        "REQUIRED",
        "PENDING",
        "POS",
        "NEG",
        "IND",
    ]
    excluded_words.extend(args.exclude)

    if repo_path:
        detect_pii_in_repo(repo_path, excluded_words, file_ext=args.ext, verbose=args.verbose)
    elif text:
        detect_pii_by_regex(text, excluded_words, verbose=args.verbose)


if __name__ == "__main__":
    main()
