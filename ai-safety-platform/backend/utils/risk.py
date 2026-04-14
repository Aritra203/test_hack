from __future__ import annotations

from backend.models.schemas import RiskLevel


def classify_risk(score: float, escalation: bool, grooming_detected: bool) -> RiskLevel:
    if grooming_detected and score >= 0.65:
        return "CRITICAL"
    if escalation and score >= 0.7:
        return "CRITICAL"
    if score >= 0.75:
        return "HIGH"
    if score >= 0.45:
        return "MEDIUM"
    return "LOW"

