"""ATS-readability and length checks based on the extracted text."""
from app.models.report import BAD, GOOD, WARN, CheckResult
from app.utils.text_utils import non_empty_lines

IDEAL_WORDS = (350, 1000)
MIN_CHARS_PER_PAGE = 300  # below this the PDF is likely a scanned image
LONG_LINE_CHARS = 220


def check_formatting(text: str, page_count: int) -> CheckResult:
    words = text.split()
    word_count = len(words)
    chars_per_page = len(text) / max(page_count, 1)
    lines = non_empty_lines(text)
    long_lines = sum(1 for line in lines if len(line) > LONG_LINE_CHARS)
    symbols = sum(1 for ch in text if not ch.isascii() and not ch.isalpha())
    symbol_ratio = symbols / max(len(text), 1)

    result = CheckResult(
        key="formatting",
        title="Formatting & ATS Readability",
        score=100,
        details={
            "word_count": word_count,
            "page_count": page_count,
            "chars_per_page": round(chars_per_page),
            "long_lines": long_lines,
            "symbol_ratio": round(symbol_ratio, 4),
        },
    )

    if chars_per_page < MIN_CHARS_PER_PAGE:
        result.score -= 50
        result.add(BAD, "Very little selectable text was found. If this is a scanned or image-based "
                        "PDF, ATS software can't read it. Export from a word processor instead.")
    else:
        result.add(GOOD, "Text is machine-readable (ATS-friendly).")

    if page_count <= 2:
        result.add(GOOD, f"Length of {page_count} page(s) is appropriate.")
    elif page_count == 3:
        result.score -= 15
        result.add(WARN, "3 pages is long. Aim for 1-2 pages unless you're very senior.")
    else:
        result.score -= 30
        result.add(BAD, f"{page_count} pages is too long. Trim to the most relevant 1-2 pages.")

    low, high = IDEAL_WORDS
    if word_count < low:
        result.score -= 20
        result.add(WARN, f"Only {word_count} words. Add more detail about your impact.")
    elif word_count > high:
        result.score -= 10
        result.add(WARN, f"{word_count} words is wordy. Tighten bullets to their strongest points.")
    else:
        result.add(GOOD, f"Word count ({word_count}) is in the ideal range.")

    if long_lines > 3:
        result.score -= 10
        result.add(WARN, "Several dense paragraphs detected. Break them into bullets.")

    if symbol_ratio > 0.03:
        result.score -= 10
        result.add(WARN, "Lots of special symbols or icons. Some ATS parsers garble these.")

    result.score = max(0, result.score)
    return result
