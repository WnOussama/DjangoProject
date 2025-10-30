import re


_BANNED_WORDS = {
    # minimal demo list; extend as needed
    "idiot", "dumb", "stupid", "hate", "kill", "racist", "sexist",
}

_BANNED_PATTERNS = [
    re.compile(r"\b(fu+|f\*+|f\W*u\W*c\W*k)\b", re.IGNORECASE),
    re.compile(r"\b(a\W*s\W*s\W*h\W*o\W*l\W*e)\b", re.IGNORECASE),
]


def is_toxic_text(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    # word list
    for w in _BANNED_WORDS:
        if f" {w} " in f" {lowered} ":
            return True
    # regex patterns
    for pat in _BANNED_PATTERNS:
        if pat.search(text):
            return True
    # excessive caps may signal shouting; ignore short texts
    letters = [ch for ch in text if ch.isalpha()]
    if len(letters) >= 8:
        caps_ratio = sum(1 for ch in letters if ch.isupper()) / len(letters)
        if caps_ratio > 0.85:
            return True
    return False


