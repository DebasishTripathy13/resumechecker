"""PDF text extraction. Works entirely in memory; uploads are never written to disk."""
import logging
from dataclasses import dataclass
from typing import IO

from pypdf import PdfReader

from app.utils.text_utils import normalize_text

log = logging.getLogger(__name__)


class PDFParseError(Exception):
    """Raised with a user-safe message when a PDF can't be processed."""


@dataclass
class ParsedPDF:
    text: str
    page_count: int


def parse_pdf(stream: IO[bytes], max_pages: int = 10) -> ParsedPDF:
    try:
        reader = PdfReader(stream)
    except Exception as exc:  # pypdf raises many types for malformed input
        log.info("PDF open failed: %s", exc)
        raise PDFParseError("The file could not be read as a PDF. It may be corrupted.") from exc

    if reader.is_encrypted:
        try:
            unlocked = reader.decrypt("")
        except Exception:
            unlocked = 0
        if not unlocked:
            raise PDFParseError("This PDF is password-protected. Remove the password and try again.")

    page_count = len(reader.pages)
    if page_count == 0:
        raise PDFParseError("The PDF has no pages.")
    if page_count > max_pages:
        raise PDFParseError(
            f"The PDF has {page_count} pages; the limit is {max_pages}. "
            "Resumes should usually be 1-2 pages."
        )

    parts = []
    for index, page in enumerate(reader.pages):
        try:
            parts.append(page.extract_text() or "")
        except Exception as exc:
            log.info("Text extraction failed on page %d: %s", index + 1, exc)
            parts.append("")

    return ParsedPDF(text=normalize_text("\n".join(parts)), page_count=page_count)
