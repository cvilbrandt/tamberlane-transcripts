import os
import re
from glob import glob
from math import inf


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
}


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
                clean_transcript(filepath)


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


def clean_transcript(path: str):
    with open(path, "rb") as f:
        text = f.read().strip()
        if not text:
            return ""
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError:
            text = text.decode("latin-1")
    
    old_text = text
    text = text.replace("&#160;", "&nbsp;")
    # Convert unicode characters of format &#160; to \xa0
    for m in re.finditer(r"&#(\d+);", text):
        text = text.replace(m.group(0), chr(int(m.group(1))))
    # Use actual unicode characters, no need for HTML escapes
    for k, v in UNICODE_REPLACEMENTS.items():
        text = text.replace(k, v)

    if old_text != text:
        with open(path, "wb") as f:
            f.write(text.encode("utf-8"))


if __name__ == "__main__":
    main()
