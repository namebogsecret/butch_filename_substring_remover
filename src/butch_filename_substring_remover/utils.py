
def remove_substrings(s: str, to_remove: set[str]) -> str:
    """Removes all substrings from the string s if they are present in the set to_remove.
    The removal is case-insensitive but preserves the original case of the remaining characters.

    Args:
        s: The string to remove substrings from.
        to_remove: A set of substrings to remove from the string s.

    Returns:
        String with all occurrences of substrings removed, with original case preserved.
    """
    import re

    for substring in to_remove:
        if not substring:  # Skip empty substrings
            continue
        # Use regex with IGNORECASE flag to find and remove all occurrences
        # while preserving the case of non-matching parts
        pattern = re.escape(substring)
        s = re.sub(pattern, '', s, flags=re.IGNORECASE)
    return s

def color_text(text, color_code):
    return f"\033[{color_code}m{text}\033[0m"