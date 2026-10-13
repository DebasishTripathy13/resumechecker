"""Combines individual check scores into an overall score and grade."""
from app.models.report import CheckResult

WEIGHTS = {
    "contact": 0.15,
    "sections": 0.20,
    "content": 0.25,
    "formatting": 0.15,
    "keywords": 0.25,
}

GRADES = (
    (85, "A", "Excellent - this resume is ready to send."),
    (70, "B", "Good - a few tweaks will make it stronger."),
    (55, "C", "Fair - address the issues below before applying."),
    (0, "D", "Needs work - focus on the high-priority fixes first."),
)


def overall_score(checks: list[CheckResult]) -> int:
    total_weight = sum(WEIGHTS.get(c.key, 0) for c in checks)
    if not total_weight:
        return 0
    weighted = sum(c.score * WEIGHTS.get(c.key, 0) for c in checks)
    return round(weighted / total_weight)


def grade_for(score: int) -> tuple[str, str]:
    for threshold, letter, verdict in GRADES:
        if score >= threshold:
            return letter, verdict
    return GRADES[-1][1], GRADES[-1][2]
