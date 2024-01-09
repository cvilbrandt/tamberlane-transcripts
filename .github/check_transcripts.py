import os
import re
import sys
from difflib import unified_diff
from glob import glob
from math import inf

from lxml.html.clean import clean
from markdown2 import Markdown
from tidylib import tidy_fragment

MARKDOWN = Markdown(extras=["strike", "break-on-newline"])

IGNORABLE_HTML_ERRORS = {
    "Warning: missing <!DOCTYPE> declaration",
    "Warning: inserting missing 'title' element",
}

UNICODE_REPLACEMENTS = {
    "&agrave;": "à",
    "&acirc;": "â",
    "&eacute;": "é",
    "&egrave;": "è",
    "&ecirc;": "ê",
    "&icirc;": "î",
    "&ocirc;": "ô",
    "&oelig;": "œ",
    "&ugrave;": "ù",
    "&ucirc;": "û",
    "&ccedil;": "ç",
    "&Agrave;": "À",
    "&Acirc;": "Â",
    "&Eacute;": "É",
    "&Egrave;": "È",
    "&Ecirc;": "Ê",
    "&Icirc;": "Î",
    "&Ocirc;": "Ô",
    "&Ccedil;": "Ç",
    "&nbsp;": " ",
}


def convert_transcript(path: str) -> str:
    with open(path, "rb") as f:
        text = f.read().strip()
        if not text:
            return ""
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError:
            text = text.decode("latin-1")
        return MARKDOWN.convert(text)


def validate_and_clean_transcript(path):
    print(path)
    html = convert_transcript(path)
    if not html:
        return
    validate_html(path, html)
    clean_html(path, html)


def validate_html(path: str, html: str):
    document, errors = tidy_fragment(html)
    for error in errors.split("\n"):
        if not error:
            continue
        error_msg = error.split("-", maxsplit=1)[1].strip()
        if error_msg not in IGNORABLE_HTML_ERRORS:
            print(html, file=sys.stderr)
            raise AssertionError(f"HTML Validation error for {path}: {error}")


def clean_html(path: str, html: str):
    """Run the converted HTML through a cleaner, to verify there were no malicious <script> tags or the like."""
    html = html.replace("<br />", "<br>")
    # Convert unicode characters of format &#160; to \xa0
    for m in re.finditer(r"&#(\d+);", html):
        html = html.replace(m.group(0), chr(int(m.group(1))))
    # Use actual unicode characters, no need for HTML escapes
    for k, v in UNICODE_REPLACEMENTS.items():
        html = html.replace(k, v)

    cleaned_html = clean.clean_html(html)
    # Remove <div> tags from start and end
    if cleaned_html.startswith("<div>"):
        cleaned_html = cleaned_html[5:-6]

    diff = list(unified_diff(html.split("\n"), cleaned_html.split("\n")))
    if diff:
        for d in diff:
            print(d)
        raise AssertionError(f"HTML cleaner removed some tags from {path}")


def sort_key(x):
    """
    Prioritize sorting folder names by their numeric value, but allow for sorting by non-numeric if the folder name
    isn't a number.
    :param x:
    :return:
    """
    try:
        i = int(x)
    except ValueError:
        i = inf
    return i, x


def main():
    folders = sorted(glob("*"), key=sort_key)
    for folder_path in folders:
        if not os.path.isdir(folder_path):
            continue
        if folder_path.endswith(".github") or folder_path.endswith("venv"):
            continue
        for ext in (".txt", ".md"):
            folder_glob = os.path.join(folder_path, f"*{ext}")
            for filepath in glob(folder_glob):
                validate_and_clean_transcript(filepath)


if __name__ == '__main__':
    main()
