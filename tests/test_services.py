import io

import pytest

from app.services import PDFParseError, ResumeAnalyzer
from app.services.contact_extractor import extract_contact
from app.services.content_analyzer import analyze_content
from app.services.keyword_matcher import check_keywords, extract_job_keywords
from app.services.pdf_parser import parse_pdf
from app.services.scorer import grade_for
from app.services.section_detector import detect_sections
from tests.conftest import make_pdf


def test_parse_pdf_extracts_text(strong_pdf):
    parsed = parse_pdf(io.BytesIO(strong_pdf))
    assert parsed.page_count == 1
    assert "Jane Doe" in parsed.text


def test_parse_pdf_rejects_too_many_pages():
    with pytest.raises(PDFParseError, match="limit"):
        parse_pdf(io.BytesIO(make_pdf(["x"], pages=4)), max_pages=3)


def test_parse_pdf_rejects_garbage():
    with pytest.raises(PDFParseError):
        parse_pdf(io.BytesIO(b"%PDF-1.4 not really a pdf"))


def test_extract_contact():
    contact = extract_contact(
        "Jane jane@x.io +1 (415) 555-0134 linkedin.com/in/jane github.com/jane janedoe.dev"
    )
    assert contact["email"] == "jane@x.io"
    assert contact["phone"]
    assert contact["linkedin"] == "linkedin.com/in/jane"
    assert contact["github"] == "github.com/jane"
    assert contact["website"] == "janedoe.dev"


def test_detect_sections():
    text = "Summary\nfoo\nWORK EXPERIENCE\nbar\nEducation:\nbaz\nTechnical Skills\nqux"
    assert detect_sections(text) == ["summary", "experience", "education", "skills"]


def test_long_lines_are_not_headings():
    assert detect_sections("I have a lot of experience in many things across the industry") == []


def test_analyze_content_counts_metrics_and_weak_phrases():
    stats = analyze_content("- Led a team of 5 engineers\n- Reduced costs by 30%\nI was responsible for testing")
    assert stats["bullet_count"] == 2
    assert stats["verb_led_bullets"] == 2
    assert stats["quantified_lines"] == 2
    assert "responsible for" in stats["weak_phrases"]
    assert stats["pronoun_count"] == 1


def test_job_keywords_prefer_known_skills():
    keywords = extract_job_keywords("We need Python and Kubernetes experience. Python is a must. Node.js plus.")
    assert set(keywords[:3]) == {"python", "node.js", "kubernetes"}
    assert "experience" not in keywords


def test_keyword_match_scoring():
    result = check_keywords("I know python and docker", "python docker kubernetes")
    match = result.details["job_match"]
    assert set(match["matched"]) == {"python", "docker"}
    assert match["missing"] == ["kubernetes"]
    assert result.score == 67


def test_grades():
    assert grade_for(90)[0] == "A"
    assert grade_for(72)[0] == "B"
    assert grade_for(60)[0] == "C"
    assert grade_for(10)[0] == "D"


def test_strong_resume_beats_weak_resume(strong_pdf, weak_pdf):
    analyzer = ResumeAnalyzer()
    strong = analyzer.analyze(io.BytesIO(strong_pdf), "strong.pdf")
    weak = analyzer.analyze(io.BytesIO(weak_pdf), "weak.pdf")
    assert strong.overall_score >= 70
    assert weak.overall_score < 40
    assert weak.suggestions[0].level == "bad"
