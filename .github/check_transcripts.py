import os
import sys
from glob import glob
from math import inf

from markdown2 import Markdown
from tidylib import tidy_fragment

MARKDOWN = Markdown(extras=["strike", "break-on-newline"])

IGNORABLE_HTML_ERRORS = {
    "Warning: missing <!DOCTYPE> declaration",
    "Warning: inserting missing 'title' element",
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


def validate_html(path):
    print(path)
    html = convert_transcript(path)
    if not html:
        return
    document, errors = tidy_fragment(html)
    for error in errors.split("\n"):
        if not error:
            continue
        error_msg = error.split("-", maxsplit=1)[1].strip()
        if error_msg not in IGNORABLE_HTML_ERRORS:
            print(html, file=sys.stderr)
            raise AssertionError(f"HTML Validation error for {path}: {error}")


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
                validate_html(filepath)


if __name__ == '__main__':
    main()
