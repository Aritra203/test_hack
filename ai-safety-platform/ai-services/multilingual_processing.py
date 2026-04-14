from __future__ import annotations

from dataclasses import dataclass


NORMALIZATION_MAP = {
    "maar dunga": "kill you",
    "toke mere felbo": "i will beat you",
    "tor jibon shesh": "your life is over",
    "bhenchod": "abusive term",
    "harami": "abusive term",
    "chod debo": "sexual threat",
}


@dataclass
class MultilingualOutput:
    normalized_text: str
    detected_language: str


def normalize_multilingual(text: str, language_hint: str | None = None) -> MultilingualOutput:
    lowered = text.lower()
    normalized = lowered
    for source, target in NORMALIZATION_MAP.items():
        normalized = normalized.replace(source, target)

    detected = language_hint or "en"
    if any(token in lowered for token in ["tum", "mera", "dunga", "nahi", "hai"]):
        detected = "hinglish"
    if any(token in lowered for token in ["toke", "tor", "ami", "tumi", "felbo"]):
        detected = "bengali-mix"
    if any(token in lowered for token in ["तुम", "मार", "नहीं", "करूंगा"]):
        detected = "hindi"

    return MultilingualOutput(
        normalized_text=normalized,
        detected_language=detected,
    )

