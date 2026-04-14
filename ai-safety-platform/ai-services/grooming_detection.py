from __future__ import annotations

from dataclasses import dataclass


GROOMING_PATTERNS = [
    "don't tell your parents",
    "secret chat",
    "send private photo",
    "meet alone",
    "you are mature for your age",
    "i can gift you",
]


@dataclass
class GroomingOutput:
    detected: bool
    signals: list[str]
    score_boost: float


def detect_grooming(text: str, previous_messages: list[dict], subject_is_minor: bool) -> GroomingOutput:
    blob = (text + " " + " ".join(str(m.get("message", "")) for m in previous_messages)).lower()
    hits = [pattern for pattern in GROOMING_PATTERNS if pattern in blob]

    if not hits:
        return GroomingOutput(detected=False, signals=[], score_boost=0.0)

    severity = 0.15 + min(0.35, 0.08 * len(hits))
    if subject_is_minor:
        severity += 0.2

    return GroomingOutput(
        detected=True,
        signals=hits,
        score_boost=round(min(severity, 0.6), 4),
    )

