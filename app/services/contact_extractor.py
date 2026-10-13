"""Finds contact details and scores their completeness."""
import re

from app.models.report import BAD, GOOD, WARN, CheckResult

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[\s.\-]?)?(?:\(?\d{2,4}\)?[\s.\-]?)?\d{3,4}[\s.\-]?\d{3,4}")
LINKEDIN_RE = re.compile(r"linkedin\.com/in/[A-Za-z0-9_\-%]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[A-Za-z0-9_\-]+", re.I)
URL_RE = re.compile(r"(?:https?://)?(?:www\.)?[A-Za-z0-9\-]+\.(?:com|io|dev|me|net|org|app|tech|site)(?:/\S*)?", re.I)


def _find_phone(text: str) -> str | None:
    for match in PHONE_RE.finditer(text):
        digits = re.sub(r"\D", "", match.group())
        if 10 <= len(digits) <= 15:
            return match.group().strip()
    return None


def extract_contact(text: str) -> dict[str, str | None]:
    email = EMAIL_RE.search(text)
    linkedin = LINKEDIN_RE.search(text)
    github = GITHUB_RE.search(text)

    website = None
    for match in URL_RE.finditer(text):
        candidate = match.group()
        lowered = candidate.lower()
        if "linkedin.com" in lowered or "github.com" in lowered:
            continue
        if email and candidate in email.group():
            continue
        website = candidate
        break

    return {
        "email": email.group() if email else None,
        "phone": _find_phone(text),
        "linkedin": linkedin.group() if linkedin else None,
        "github": github.group() if github else None,
        "website": website,
    }


def check_contact(text: str) -> CheckResult:
    contact = extract_contact(text)
    result = CheckResult(key="contact", title="Contact Information", score=0, details=contact)

    if contact["email"]:
        result.score += 40
        result.add(GOOD, "Email address found.")
    else:
        result.add(BAD, "No email address found. Recruiters need a way to reach you.")

    if contact["phone"]:
        result.score += 30
        result.add(GOOD, "Phone number found.")
    else:
        result.add(WARN, "No phone number found.")

    if contact["linkedin"]:
        result.score += 20
        result.add(GOOD, "LinkedIn profile linked.")
    else:
        result.add(WARN, "Add your LinkedIn profile URL.")

    if contact["github"] or contact["website"]:
        result.score += 10
        result.add(GOOD, "Portfolio / GitHub link found.")
    else:
        result.add(WARN, "Consider adding a portfolio or GitHub link to showcase your work.")

    return result
