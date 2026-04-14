from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


ESCALATION_TERMS = {"kill", "destroy", "leak", "viral", "ruin", "blackmail", "expose"}


@dataclass
class ContextOutput:
    escalation_detected: bool
    summary: str
    contextual_boost: float


def analyze_context(current_text: str, previous_messages: list[dict]) -> ContextOutput:
    current = current_text.lower()
    timeline: list[tuple[datetime | None, str]] = []

    for msg in previous_messages:
        ts = msg.get("timestamp")
        parsed_ts = None
        if isinstance(ts, str):
            try:
                parsed_ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                parsed_ts = None
        timeline.append((parsed_ts, str(msg.get("message", "")).lower()))

    message_blob = " ".join(content for _, content in timeline) + " " + current
    escalation_hits = sorted({term for term in ESCALATION_TERMS if term in message_blob})

    threat_density = len(escalation_hits)
    context_size = len(previous_messages)
    escalation_detected = threat_density >= 2 or (threat_density >= 1 and context_size >= 4)
    contextual_boost = min(0.25, 0.04 * context_size + 0.07 * threat_density)

    summary = (
        f"Context inspected over {context_size} prior messages. "
        f"Escalation terms found: {', '.join(escalation_hits) if escalation_hits else 'none'}."
    )

    return ContextOutput(
        escalation_detected=escalation_detected,
        summary=summary,
        contextual_boost=round(contextual_boost, 4),
    )

