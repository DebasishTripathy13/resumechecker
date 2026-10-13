"""Skill detection and job-description keyword matching."""
from collections import Counter

from app.data.keywords import SOFT_SKILLS, STOPWORDS, TECH_SKILLS
from app.models.report import BAD, GOOD, WARN, CheckResult
from app.utils.text_utils import contains_phrase, tokenize

MAX_JD_KEYWORDS = 30
MIN_KEYWORD_LEN = 3


def detect_skills(text: str) -> dict[str, list[str]]:
    lowered = text.lower()
    return {
        "technical": [s for s in TECH_SKILLS if contains_phrase(lowered, s)],
        "soft": [s for s in SOFT_SKILLS if contains_phrase(lowered, s)],
    }


def extract_job_keywords(job_description: str, limit: int = MAX_JD_KEYWORDS) -> list[str]:
    """Known skills first, then the most frequent meaningful words."""
    lowered = job_description.lower()
    known = [s for s in (*TECH_SKILLS, *SOFT_SKILLS) if contains_phrase(lowered, s)]
    known_parts = {part for skill in known for part in skill.split()}

    counts = Counter(
        token for token in tokenize(job_description)
        if len(token) >= MIN_KEYWORD_LEN
        and token not in STOPWORDS
        and token not in known_parts
        and not token.isdigit()
    )
    frequent = [word for word, _ in counts.most_common() if word not in known]
    return (known + frequent)[:limit]


def check_keywords(text: str, job_description: str | None) -> CheckResult:
    skills = detect_skills(text)

    if not job_description or not job_description.strip():
        score = min(100, len(skills["technical"]) * 10 + len(skills["soft"]) * 5)
        result = CheckResult(key="keywords", title="Skills & Keywords", score=score,
                             details={"skills": skills, "job_match": None})
        if skills["technical"]:
            result.add(GOOD, f"Detected {len(skills['technical'])} technical skills.")
        else:
            result.add(WARN, "No common technical skills detected. List tools and technologies explicitly.")
        result.add(WARN, "Paste a job description to see how well you match a specific role.")
        return result

    keywords = extract_job_keywords(job_description)
    lowered = text.lower()
    matched = [k for k in keywords if contains_phrase(lowered, k)]
    missing = [k for k in keywords if k not in matched]
    score = round(100 * len(matched) / len(keywords)) if keywords else 0

    result = CheckResult(
        key="keywords",
        title="Job Description Match",
        score=score,
        details={
            "skills": skills,
            "job_match": {"keywords": keywords, "matched": matched, "missing": missing},
        },
    )
    if not keywords:
        result.add(WARN, "Couldn't extract keywords from the job description.")
    elif score >= 75:
        result.add(GOOD, f"Strong match: {len(matched)} of {len(keywords)} job keywords found.")
    elif score >= 50:
        result.add(WARN, f"Partial match: {len(matched)} of {len(keywords)} keywords. "
                         "Work the missing ones in where truthful.")
    else:
        result.add(BAD, f"Weak match: only {len(matched)} of {len(keywords)} keywords found.")
    if missing:
        result.add(WARN, "Missing keywords: " + ", ".join(missing[:10]) + ("..." if len(missing) > 10 else ""))
    return result
