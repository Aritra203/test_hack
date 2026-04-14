from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from backend.config.settings import settings
from backend.models.schemas import AnalysisResultPayload, ExplainableSpan, LabelScore
from backend.utils.legal_mapping import map_to_indian_laws
from backend.utils.module_loader import load_module_from_path
from backend.utils.risk import classify_risk


AI_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ai-services"


def _load_callable(module_name: str, file_name: str, attr_name: str) -> Any:
    module = load_module_from_path(module_name, AI_SERVICES_DIR / file_name)
    callable_obj = getattr(module, attr_name, None)
    if callable_obj is None:
        raise RuntimeError(f"{attr_name} not found in ai-services/{file_name}")
    return callable_obj


class SafetyAnalysisService:
    def __init__(self) -> None:
        toxicity_cls = _load_callable("ai_services_toxicity", "toxicity.py", "ToxicityAnalyzer")
        self._toxicity_analyzer = toxicity_cls(model_name=settings.hf_model_name)
        self._normalize = _load_callable(
            "ai_services_multilingual", "multilingual_processing.py", "normalize_multilingual"
        )
        self._context = _load_callable("ai_services_context", "context_analysis.py", "analyze_context")
        self._grooming = _load_callable("ai_services_grooming", "grooming_detection.py", "detect_grooming")

    def analyze(
        self,
        text: str,
        previous_messages: list[dict],
        language_hint: str | None,
        subject_is_minor: bool,
    ) -> AnalysisResultPayload:
        normalized = self._normalize(text, language_hint)
        context_out = self._context(normalized.normalized_text, previous_messages)
        toxicity_out = self._toxicity_analyzer.score_text(normalized.normalized_text)
        grooming_out = self._grooming(normalized.normalized_text, previous_messages, subject_is_minor)

        blended_score = min(
            1.0,
            toxicity_out.toxicity_score + context_out.contextual_boost + grooming_out.score_boost,
        )
        risk = classify_risk(
            score=blended_score,
            escalation=context_out.escalation_detected,
            grooming_detected=grooming_out.detected,
        )

        labels = [
            LabelScore(label="cyberbullying", score=toxicity_out.label_scores["cyberbullying"]),
            LabelScore(label="threat", score=toxicity_out.label_scores["threat"]),
            LabelScore(label="hate_speech", score=toxicity_out.label_scores["hate_speech"]),
            LabelScore(label="sexual_harassment", score=toxicity_out.label_scores["sexual_harassment"]),
        ]

        explain_spans = [ExplainableSpan(term=item["term"], reason=item["reason"]) for item in toxicity_out.explainable_spans]
        legal_sections = map_to_indian_laws(
            label_scores=toxicity_out.label_scores,
            grooming_signals=grooming_out.signals,
            is_minor=subject_is_minor,
        )

        return AnalysisResultPayload(
            toxicity_score=round(blended_score, 4),
            risk_level=risk,
            labels=labels,
            explainable_spans=explain_spans,
            normalized_text=normalized.normalized_text,
            detected_language=normalized.detected_language,
            grooming_signals=grooming_out.signals,
            context_summary=context_out.summary,
            escalation_detected=context_out.escalation_detected,
            legal_sections=legal_sections,
        )


@lru_cache(maxsize=1)
def get_safety_analysis_service() -> SafetyAnalysisService:
    return SafetyAnalysisService()

