from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any

from transformers import pipeline


TARGET_LABELS = ["cyberbullying", "threat", "hate_speech", "sexual_harassment"]


RULE_LEXICON: dict[str, list[str]] = {
    "cyberbullying": ["loser", "idiot", "worthless", "stupid", "ugly", "shame on you"],
    "threat": ["kill", "hurt", "attack", "destroy you", "beat you", "end you"],
    "hate_speech": ["dirty race", "inferior", "go back", "vermin", "terrorist pig"],
    "sexual_harassment": ["nudes", "send pics", "touch you", "sexy kid", "explicit photo"],
}


@dataclass
class ToxicityOutput:
    label_scores: dict[str, float]
    toxicity_score: float
    explainable_spans: list[dict[str, str]]
    reasoning: str


class ToxicityAnalyzer:
    def __init__(self, model_name: str = "unitary/toxic-bert") -> None:
        self._classifier = pipeline(
            task="text-classification",
            model=model_name,
            top_k=None,
        )

    def _ml_score(self, text: str) -> float:
        results = self._classifier(text, truncation=True, max_length=512)
        if not results:
            return 0.0
        first = results[0] if isinstance(results[0], list) else results
        toxic_scores = [
            float(item.get("score", 0.0))
            for item in first
            if "toxic" in str(item.get("label", "")).lower()
            and "non" not in str(item.get("label", "")).lower()
        ]
        if toxic_scores:
            return max(toxic_scores)
        fallback = [float(item.get("score", 0.0)) for item in first]
        return max(fallback) if fallback else 0.0

    def _rule_scores(self, text: str) -> tuple[dict[str, float], list[dict[str, str]]]:
        lowered = text.lower()
        label_scores = {label: 0.0 for label in TARGET_LABELS}
        spans: list[dict[str, str]] = []

        for label, lexemes in RULE_LEXICON.items():
            hits = [lex for lex in lexemes if lex in lowered]
            if hits:
                label_scores[label] = min(1.0, 0.35 + (0.15 * len(hits)))
                for hit in hits[:4]:
                    spans.append({"term": hit, "reason": f"Matched {label.replace('_', ' ')} lexicon"})
        return label_scores, spans

    def score_text(self, text: str) -> ToxicityOutput:
        cleaned = text.strip()
        if not cleaned:
            return ToxicityOutput(
                label_scores={label: 0.0 for label in TARGET_LABELS},
                toxicity_score=0.0,
                explainable_spans=[],
                reasoning="No content provided.",
            )

        ml_score = max(0.0, min(1.0, float(self._ml_score(cleaned))))
        rule_scores, spans = self._rule_scores(cleaned)

        label_scores = {
            "cyberbullying": max(rule_scores["cyberbullying"], ml_score * 0.7),
            "threat": max(rule_scores["threat"], ml_score * 0.8),
            "hate_speech": max(rule_scores["hate_speech"], ml_score * 0.65),
            "sexual_harassment": max(rule_scores["sexual_harassment"], ml_score * 0.75),
        }

        toxicity_score = max(label_scores.values()) if label_scores else 0.0
        reasoning = (
            "Hybrid score combines transformer confidence and category-specific rule matches "
            f"(ml={ml_score:.3f}, max_rule={max(rule_scores.values()):.3f})."
        )

        return ToxicityOutput(
            label_scores={k: round(v, 4) for k, v in label_scores.items()},
            toxicity_score=round(toxicity_score, 4),
            explainable_spans=spans,
            reasoning=reasoning,
        )


@lru_cache(maxsize=1)
def get_toxicity_analyzer(model_name: str = "unitary/toxic-bert") -> ToxicityAnalyzer:
    return ToxicityAnalyzer(model_name=model_name)

