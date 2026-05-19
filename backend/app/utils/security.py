import re
from typing import Optional


MAX_TRANSCRIPT_LENGTH = 50000


def sanitize_transcript(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[<>]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def validate_transcript_length(text: str) -> Optional[str]:
    length = len(text)
    if length == 0:
        return "Transcript cannot be empty."
    if length > MAX_TRANSCRIPT_LENGTH:
        return f"Transcript exceeds maximum length of {MAX_TRANSCRIPT_LENGTH} characters."
    return None
