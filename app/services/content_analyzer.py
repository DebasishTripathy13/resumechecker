"""Scores writing quality: action verbs, quantified impact, weak phrasing."""
import re

from app.data.keywords import ACTION_VERBS, WEAK_PHRASES
from app.models.report import BAD, GOOD, WARN, CheckResult
from app.utils.text_utils import contains_phrase, is_bullet, non_empty_lines, strip_bullet

# A metric: a percentage, currency amount, multiplier, or a number followed by a unit of impact.
QUANTIFIED_RE = re.compile(
    r"\d+(?:\.\d+)?\s?%"
    r"|[$€£₹]\s?\d"
    r"|\b\d+(?:\.\d+)?x\b"
    r"|\b\d[\d,.]*\+?\s?(?:k|m|million|billion|thousand|users|customers|clients|"
    r"people|engineers|members|hours|days|weeks|requests|transactions|projects|teams)\b",
    re.I,
)
PRONOUN_RE = re.compile(r"\b(?:I|me|my|myself)\b")

TARGET_VERBS = 8
TARGET_QUANTIFIED = 5
TARGET_BULLETS = 8


def analyze_content(text: str) -> dict:
    lines = non_empty_lines(text)
    bullets = [strip_bullet(line) for line in lines if is_bullet(line)]

    verbs_used: set[str] = set()
    verb_led_bullets = 0
    for bullet in bullets:
        first_word = bullet.split(" ", 1)[0].lower().strip(",.;:")
        if first_word in ACTION_VERBS:
            verb_led_bullets += 1
    for word in re.findall(r"[a-z]+", text.lower()):
        if word in ACTION_VERBS:
            verbs_used.add(word)

    lowered = text.lower()
    return {
        "bullet_count": len(bullets),
        "action_verbs": sorted(verbs_used),
        "verb_led_bullets": verb_led_bullets,
        "quantified_lines": sum(1 for line in lines if QUANTIFIED_RE.search(line)),
        "weak_phrases": [p for p in WEAK_PHRASES if contains_phrase(lowered, p)],
        "pronoun_count": len(PRONOUN_RE.findall(text)),
    }


def check_content(text: str) -> CheckResult:
    stats = analyze_content(text)
    result = CheckResult(key="content", title="Content & Impact", score=0, details=stats)

    verb_count = len(stats["action_verbs"])
    verb_score = min(verb_count / TARGET_VERBS, 1) * 35
    quant_score = min(stats["quantified_lines"] / TARGET_QUANTIFIED, 1) * 35
    bullet_score = min(stats["bullet_count"] / TARGET_BULLETS, 1) * 30
    penalty = min(len(stats["weak_phrases"]) * 5, 15) + min(stats["pronoun_count"] * 2, 10)
    result.score = max(0, round(verb_score + quant_score + bullet_score - penalty))

    if verb_count >= TARGET_VERBS:
        result.add(GOOD, f"Strong use of action verbs ({verb_count} distinct).")
    elif verb_count >= 3:
        result.add(WARN, f"Only {verb_count} distinct action verbs. Start bullets with words like "
                         "'Led', 'Built', 'Reduced'.")
    else:
        result.add(BAD, "Very few action verbs. Start each bullet with a strong verb.")

    quantified = stats["quantified_lines"]
    if quantified >= TARGET_QUANTIFIED:
        result.add(GOOD, f"{quantified} lines include measurable results.")
    elif quantified > 0:
        result.add(WARN, f"Only {quantified} lines include metrics. Quantify impact "
                         "(%, $, users, time saved).")
    else:
        result.add(BAD, "No quantified achievements found. Numbers make impact concrete.")

    if stats["bullet_count"] >= TARGET_BULLETS:
        result.add(GOOD, "Experience is broken into readable bullet points.")
    else:
        result.add(WARN, "Use more bullet points instead of dense paragraphs.")

    if stats["weak_phrases"]:
        quoted = ", ".join(f"'{p}'" for p in stats["weak_phrases"])
        result.add(WARN, f"Replace passive phrases ({quoted}) with achievement-focused verbs.")

    if stats["pronoun_count"] > 2:
        result.add(WARN, f"Found {stats['pronoun_count']} first-person pronouns (I, me, my). "
                         "Resumes are conventionally written without them.")

    return result
