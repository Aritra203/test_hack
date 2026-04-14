from __future__ import annotations

from importlib import import_module


class ToxicityAnalyzer:
    def __init__(self, model_name: str = "unitary/toxic-bert") -> None:
        try:
            transformers_module = import_module("transformers")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "transformers is not installed. Install backend requirements before running analysis."
            ) from exc

        pipeline_factory = getattr(transformers_module, "pipeline", None)
        if pipeline_factory is None:
            raise RuntimeError("transformers.pipeline is unavailable in current environment.")

        self._classifier = pipeline_factory(
            task="text-classification",
            model=model_name,
            return_all_scores=True,
        )

    def score_text(self, text: str) -> float:
        cleaned_text = text.strip()
        if not cleaned_text:
            return 0.0

        results = self._classifier(cleaned_text, truncation=True, max_length=512)
        if not results:
            return 0.0

        scores = results[0] if isinstance(results[0], list) else results

        toxic_scores = [
            float(item.get("score", 0.0))
            for item in scores
            if "toxic" in str(item.get("label", "")).lower()
            and "non" not in str(item.get("label", "")).lower()
        ]
        if toxic_scores:
            return max(toxic_scores)

        # Fallback for models that output generic labels like LABEL_0/LABEL_1.
        label_one_score = next(
            (
                float(item.get("score", 0.0))
                for item in scores
                if str(item.get("label", "")).upper().endswith("1")
            ),
            None,
        )
        if label_one_score is not None:
            return label_one_score

        return max(float(item.get("score", 0.0)) for item in scores)
