"""Small, dependency-free text helpers."""
import re
import unicodedata

# Keeps tech tokens like "c++", "c#", "node.js" and "ci/cd" intact.
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9+#./\-]*")
_BULLET_RE = re.compile(r"^\s*(?:[•▪●◦‣⁃■\-\*–>]|\d+[.)])\s+")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[ \t ]+", " ", text)
    text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)
    return text.strip()


def tokenize(text: str) -> list[str]:
    return [t.lower().rstrip(".-/") for t in _WORD_RE.findall(text)]


def non_empty_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def is_bullet(line: str) -> bool:
    return bool(_BULLET_RE.match(line))


def strip_bullet(line: str) -> str:
    return _BULLET_RE.sub("", line, count=1).strip()


def contains_phrase(haystack_lower: str, phrase: str) -> bool:
    """Whole-word/phrase match that also works for symbols like c++ and .net."""
    pattern = r"(?<![a-z0-9])" + re.escape(phrase.lower()) + r"(?![a-z0-9+#])"
    return re.search(pattern, haystack_lower) is not None
