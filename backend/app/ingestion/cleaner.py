import re
import unicodedata


def clean_text(text: str) -> str:
    """Cleans extracted raw text while preserving readability and paragraph structure."""
    if not text:
        return ""
    # Normalize unicode (NFKC)
    text = unicodedata.normalize("NFKC", text)
    # Remove null bytes or invisible control characters (keep \n, \r, \t)
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Normalize Windows linebreaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Replace 3 or more consecutive newlines with 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Remove excessive horizontal spaces
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def detect_section_heading(text_snippet: str) -> str:
    """Heuristic to detect heading or first section from text snippet."""
    if not text_snippet:
        return "General"
    lines = [line.strip() for line in text_snippet.split("\n") if line.strip()]
    if not lines:
        return "General"
    first_line = lines[0]
    # Check if first line looks like a title/heading (starts with #, SOP-, Section, or short all-caps)
    if first_line.startswith("#"):
        return first_line.lstrip("#").strip()
    if len(first_line) <= 80 and (
        first_line.isupper()
        or first_line.lower().startswith("section")
        or first_line.lower().startswith("sop")
        or first_line.lower().startswith("policy")
        or first_line.lower().startswith("appendix")
        or ":" in first_line
    ):
        return first_line.rstrip(":")
    return "General"
