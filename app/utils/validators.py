"""Upload validation. Returns a user-facing error string, or None if valid."""
from typing import IO, Optional

from werkzeug.datastructures import FileStorage

PDF_MAGIC = b"%PDF-"


def allowed_file(filename: str, allowed_extensions: set[str]) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def has_pdf_signature(stream: IO[bytes]) -> bool:
    """Check the magic bytes without consuming the stream."""
    position = stream.tell()
    head = stream.read(1024)
    stream.seek(position)
    # The spec allows junk before the header, so search the first KB.
    return PDF_MAGIC in head


def validate_upload(file: Optional[FileStorage], allowed_extensions: set[str]) -> Optional[str]:
    if file is None or not file.filename:
        return "Please choose a PDF file to upload."
    if not allowed_file(file.filename, allowed_extensions):
        return "Only PDF files are supported."
    if not has_pdf_signature(file.stream):
        return "That file doesn't look like a valid PDF."
    return None
