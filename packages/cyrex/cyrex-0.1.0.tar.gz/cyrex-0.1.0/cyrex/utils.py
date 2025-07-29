import re

def slugify(text: str) -> str:
    """
    Make a filename-safe slug from a string.
    e.g., "main.py" → "main_py"
    """
    return re.sub(r'[^\w]+', '_', text)


def strip_ansi(text: str) -> str:
    """
    Remove ANSI color codes from a string (optional).
    """
    ansi_escape = re.compile(r'(?:\x1B[@-_][0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)
