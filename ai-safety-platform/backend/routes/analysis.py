from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from backend.config.database import db_manager
from backend.config.settings import settings
from backend.models.db_models import build_analysis_record
from backend.models.schemas import ImageAnalysisResponse, TextAnalysisRequest, TextAnalysisResponse
from backend.services.cloudinary_service import cloudinary_upload_service
from backend.services.ocr_service import ocr_service
from backend.services.toxicity_service import get_safety_analysis_service


router = APIRouter(tags=["analysis"])
analysis_service = get_safety_analysis_service()


@router.post("/analyze-text", response_model=TextAnalysisResponse)
async def analyze_text(payload: TextAnalysisRequest) -> TextAnalysisResponse:
    analyzed_text = payload.text.strip()
    if not analyzed_text:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Text cannot be empty.")

    result = analysis_service.analyze(
        text=analyzed_text,
        previous_messages=[item.model_dump() for item in payload.previous_messages],
        language_hint=payload.language_hint,
        subject_is_minor=payload.subject_is_minor,
    )

    record = build_analysis_record(source_type="text", analyzed_text=analyzed_text, result=result)
    insert_result = await db_manager.get_database()["analyses"].insert_one(record)
    created_at = record["created_at"]

    return TextAnalysisResponse(
        analysis_id=str(insert_result.inserted_id),
        analyzed_text=analyzed_text,
        result=result,
        created_at=created_at,
    )


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    subject_is_minor: bool = False,
    language_hint: str | None = None,
) -> ImageAnalysisResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only image uploads are supported.")

    upload = await cloudinary_upload_service.upload_fastapi_file(
        file=file,
        folder_override=f"{settings.cloudinary_folder}/images",
    )
    extracted_text = ocr_service.extract_text_from_bytes(upload.content)

    result = analysis_service.analyze(
        text=extracted_text,
        previous_messages=[],
        language_hint=language_hint,
        subject_is_minor=subject_is_minor,
    )

    record = build_analysis_record(
        source_type="image",
        analyzed_text=extracted_text,
        result=result,
        cloudinary_url=upload.url,
        cloudinary_public_id=upload.public_id,
    )
    insert_result = await db_manager.get_database()["analyses"].insert_one(record)
    created_at = record["created_at"]

    return ImageAnalysisResponse(
        evidence_id=str(insert_result.inserted_id),
        extracted_text=extracted_text,
        cloudinary_url=upload.url,
        cloudinary_public_id=upload.public_id,
        result=result,
        created_at=created_at,
    )

