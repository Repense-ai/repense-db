import re


def extract_list_from_str(text):
    pattern = r"\[.*?\]"
    match = re.search(pattern, text)
    if match:
        return match.group(0)
    return None
