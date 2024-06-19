
def remove_substrings(s: str, to_remove: set[str]) -> str:
    """Removes all substrings from the string s if they are present in the set to_remove.
    s: The string to remove substrings from.
    to_remove: A set of substrings to remove from the string s."""
    for substring in to_remove:
        if s.lower().startswith(substring.lower()):
            s = s.lower().replace(substring.lower(), "", 1)
    return s

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"