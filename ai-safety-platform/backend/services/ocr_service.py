from __future__ import annotations

import io

import pytesseract
from PIL import Image, UnidentifiedImageError

from backend.config.settings import settings


class OCRService:
    def __init__(self) -> None:
        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    def extract_text_from_bytes(self, content: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(content))
        except UnidentifiedImageError as exc:
            raise ValueError("Uploaded file is not a valid image.") from exc
        return " ".join(pytesseract.image_to_string(image).split())


ocr_service = OCRService()

