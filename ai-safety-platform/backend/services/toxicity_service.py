from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Type

from fastapi import HTTPException, status

from backend.config.settings import settings
from backend.utils.module_loader import load_module_from_path


AI_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ai-services"
TOXICITY_MODULE_PATH = AI_SERVICES_DIR / "toxicity.py"


def _get_toxicity_analyzer_class() -> Type[Any]:
    module = load_module_from_path("ai_services_toxicity", TOXICITY_MODULE_PATH)
    toxicity_cls = getattr(module, "ToxicityAnalyzer", None)
    if toxicity_cls is None:
        raise RuntimeError("ToxicityAnalyzer class not found in ai-services/toxicity.py")
    return toxicity_cls


class ToxicityService:
    def __init__(self) -> None:
        toxicity_analyzer_cls = _get_toxicity_analyzer_class()
        self._analyzer = toxicity_analyzer_cls(model_name=settings.hf_model_name)

    def analyze_text(self, text: str) -> float:
        cleaned_text = text.strip()
        if not cleaned_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Text cannot be empty.",
            )

        try:
            score = float(self._analyzer.score_text(cleaned_text))
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Toxicity model error: {exc}",
            ) from exc

        score = max(0.0, min(1.0, score))
        return round(score, 4)


@lru_cache(maxsize=1)
def get_toxicity_service() -> ToxicityService:
    return ToxicityService()
