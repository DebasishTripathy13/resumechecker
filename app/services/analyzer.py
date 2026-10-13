"""Orchestrates parsing and every check into a single AnalysisReport."""
from typing import IO, Any, Mapping

from app.models.report import AnalysisReport
from app.services.contact_extractor import check_contact
from app.services.content_analyzer import check_content
from app.services.formatting_checker import check_formatting
from app.services.keyword_matcher import check_keywords
from app.services.pdf_parser import parse_pdf
from app.services.scorer import grade_for, overall_score
from app.services.section_detector import check_sections

PREVIEW_CHARS = 3000


class ResumeAnalyzer:
    def __init__(self, max_pages: int = 10, max_jd_chars: int = 20_000):
        self.max_pages = max_pages
        self.max_jd_chars = max_jd_chars

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "ResumeAnalyzer":
        return cls(max_pages=config["MAX_PDF_PAGES"], max_jd_chars=config["MAX_JOB_DESCRIPTION_CHARS"])

    def analyze(self, stream: IO[bytes], filename: str, job_description: str | None = None) -> AnalysisReport:
        parsed = parse_pdf(stream, max_pages=self.max_pages)
        text = parsed.text
        jd = (job_description or "")[: self.max_jd_chars]

        checks = [
            check_contact(text),
            check_sections(text),
            check_content(text),
            check_formatting(text, parsed.page_count),
            check_keywords(text, jd),
        ]
        score = overall_score(checks)
        grade, verdict = grade_for(score)

        return AnalysisReport(
            filename=filename,
            page_count=parsed.page_count,
            word_count=len(text.split()),
            overall_score=score,
            grade=grade,
            verdict=verdict,
            checks=checks,
            text_preview=text[:PREVIEW_CHARS],
        )
