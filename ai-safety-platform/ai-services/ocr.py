from __future__ import annotations

import io
from importlib import import_module


def _load_ocr_modules():
    try:
        pytesseract_module = import_module("pytesseract")
        requests_module = import_module("requests")
        pil_module = import_module("PIL.Image")
        pil_errors_module = import_module("PIL")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "OCR dependencies are missing. Install backend requirements before running OCR."
        ) from exc

    image_open = getattr(pil_module, "open")
    unidentified_error = getattr(pil_errors_module, "UnidentifiedImageError")
    return pytesseract_module, requests_module, image_open, unidentified_error


class OCRExtractor:
    def __init__(self, tesseract_cmd: str | None = None) -> None:
        pytesseract_module, _, _, _ = _load_ocr_modules()
        self._pytesseract = pytesseract_module

        if tesseract_cmd:
            self._pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def extract_text_from_image_url(self, image_url: str) -> str:
        pytesseract_module, requests_module, image_open, unidentified_error_cls = _load_ocr_modules()

        response = requests_module.get(image_url, timeout=30)
        response.raise_for_status()

        try:
            image = image_open(io.BytesIO(response.content))
        except unidentified_error_cls as exc:
            raise ValueError("Provided URL does not contain a valid image.") from exc

        try:
            extracted_text = pytesseract_module.image_to_string(image)
        except pytesseract_module.TesseractNotFoundError as exc:
            raise RuntimeError(
                "Tesseract binary not found. Install Tesseract OCR and set TESSERACT_CMD in .env."
            ) from exc

        return " ".join(extracted_text.split())
