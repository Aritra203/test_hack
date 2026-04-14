from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Type

from fastapi import HTTPException, status

from backend.config.settings import settings
from backend.utils.module_loader import load_module_from_path


AI_SERVICES_DIR = Path(__file__).resolve().parents[2] / "ai-services"
OCR_MODULE_PATH = AI_SERVICES_DIR / "ocr.py"


def _get_ocr_extractor_class() -> Type[Any]:
    module = load_module_from_path("ai_services_ocr", OCR_MODULE_PATH)
    ocr_cls = getattr(module, "OCRExtractor", None)
    if ocr_cls is None:
        raise RuntimeError("OCRExtractor class not found in ai-services/ocr.py")
    return ocr_cls


class OCRService:
    def __init__(self) -> None:
        ocr_extractor_cls = _get_ocr_extractor_class()
        self._extractor = ocr_extractor_cls(tesseract_cmd=settings.tesseract_cmd)

    def extract_text_from_image_url(self, image_url: str) -> str:
        try:
            return self._extractor.extract_text_from_image_url(image_url)
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(exc),
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"OCR failed for supplied image: {exc}",
            ) from exc


@lru_cache(maxsize=1)
def get_ocr_service() -> OCRService:
    return OCRService()
