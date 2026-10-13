"""Data structures shared between the analysis services, routes and templates."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

GOOD, WARN, BAD = "good", "warn", "bad"


@dataclass
class Finding:
    level: str  # GOOD | WARN | BAD
    message: str


@dataclass
class CheckResult:
    key: str
    title: str
    score: int  # 0-100
    findings: list[Finding] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def status(self) -> str:
        if self.score >= 75:
            return GOOD
        if self.score >= 50:
            return WARN
        return BAD

    def add(self, level: str, message: str) -> None:
        self.findings.append(Finding(level, message))

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status
        return data


@dataclass
class AnalysisReport:
    filename: str
    page_count: int
    word_count: int
    overall_score: int
    grade: str
    verdict: str
    checks: list[CheckResult]
    text_preview: str

    @property
    def suggestions(self) -> list[Finding]:
        """Actionable findings, most severe first."""
        issues = [f for c in self.checks for f in c.findings if f.level != GOOD]
        return sorted(issues, key=lambda f: f.level != BAD)

    def to_dict(self) -> dict[str, Any]:
        return {
            "filename": self.filename,
            "page_count": self.page_count,
            "word_count": self.word_count,
            "overall_score": self.overall_score,
            "grade": self.grade,
            "verdict": self.verdict,
            "checks": [c.to_dict() for c in self.checks],
            "suggestions": [asdict(s) for s in self.suggestions],
        }
