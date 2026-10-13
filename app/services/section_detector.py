"""Detects standard resume section headings."""
import re

from app.models.report import BAD, GOOD, WARN, CheckResult
from app.utils.text_utils import non_empty_lines

SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "summary": ("summary", "professional summary", "profile", "about me", "objective",
                "career objective", "professional profile"),
    "experience": ("experience", "work experience", "professional experience",
                   "employment history", "work history", "employment", "career history"),
    "education": ("education", "academic background", "academics", "qualifications",
                  "educational background"),
    "skills": ("skills", "technical skills", "core skills", "key skills", "competencies",
               "core competencies", "technologies", "tech stack", "skills & tools"),
    "projects": ("projects", "personal projects", "key projects", "academic projects",
                 "side projects"),
    "certifications": ("certifications", "certificates", "licenses",
                       "licenses & certifications", "courses"),
    "achievements": ("achievements", "awards", "honors", "accomplishments",
                     "awards & honors"),
}

REQUIRED = ("experience", "education", "skills")
RECOMMENDED = ("summary", "projects", "certifications")

_HEADING_MAX_LEN = 40


def _clean_heading(line: str) -> str:
    return re.sub(r"[^a-z& ]", "", line.lower()).strip()


def detect_sections(text: str) -> list[str]:
    alias_lookup = {alias: name for name, aliases in SECTION_ALIASES.items() for alias in aliases}
    found: list[str] = []
    for line in non_empty_lines(text):
        if len(line) > _HEADING_MAX_LEN:
            continue
        section = alias_lookup.get(_clean_heading(line))
        if section and section not in found:
            found.append(section)
    return found


def check_sections(text: str) -> CheckResult:
    found = detect_sections(text)
    missing_required = [s for s in REQUIRED if s not in found]
    missing_recommended = [s for s in RECOMMENDED if s not in found]

    result = CheckResult(
        key="sections",
        title="Resume Sections",
        score=0,
        details={
            "found": found,
            "missing_required": missing_required,
            "missing_recommended": missing_recommended,
        },
    )

    required_points = 70 * (len(REQUIRED) - len(missing_required)) / len(REQUIRED)
    recommended_points = 30 * (len(RECOMMENDED) - len(missing_recommended)) / len(RECOMMENDED)
    result.score = round(required_points + recommended_points)

    if not missing_required:
        result.add(GOOD, "All essential sections (Experience, Education, Skills) are present.")
    for name in missing_required:
        result.add(BAD, f"Missing a clear '{name.title()}' section heading. ATS systems look for it.")
    for name in missing_recommended:
        result.add(WARN, f"Consider adding a '{name.title()}' section.")

    return result
