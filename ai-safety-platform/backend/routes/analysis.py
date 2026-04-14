from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from starlette.concurrency import run_in_threadpool

from backend.config.database import db_manager
from backend.config.settings import settings
from backend.models.db_models import build_evidence_record, build_text_analysis_record
from backend.models.schemas import ImageAnalysisResponse, TextAnalysisRequest, TextAnalysisResponse
from backend.services.cloudinary_service import cloudinary_upload_service
from backend.services.ocr_service import get_ocr_service
from backend.services.toxicity_service import get_toxicity_service
from backend.utils.risk import classify_risk


router = APIRouter(tags=["analysis"])


toxicity_service = get_toxicity_service()
ocr_service = get_ocr_service()


@router.post("/analyze-text", response_model=TextAnalysisResponse)
async def analyze_text(payload: TextAnalysisRequest) -> TextAnalysisResponse:
    toxicity_score = await run_in_threadpool(toxicity_service.analyze_text, payload.text)
    risk_label = classify_risk(toxicity_score)

    database = db_manager.get_database()
    record = build_text_analysis_record(
        text=payload.text,
        toxicity_score=toxicity_score,
        risk_label=risk_label,
    )
    insert_result = await database["text_analyses"].insert_one(record)

    return TextAnalysisResponse(
        analysis_id=str(insert_result.inserted_id),
        analyzed_text=payload.text,
        toxicity_score=toxicity_score,
        risk_label=risk_label,
    )


@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)) -> ImageAnalysisResponse:
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are supported for OCR analysis.",
        )

    upload_result = await cloudinary_upload_service.upload_fastapi_file(
        file,
        folder_override=f"{settings.cloudinary_folder}/analyzed-images",
    )

    extracted_text = await run_in_threadpool(
        ocr_service.extract_text_from_image_url,
        upload_result.url,
    )

    if extracted_text.strip():
        toxicity_score = await run_in_threadpool(toxicity_service.analyze_text, extracted_text)
    else:
        toxicity_score = 0.0

    risk_label = classify_risk(toxicity_score)

    database = db_manager.get_database()
    evidence_record = build_evidence_record(
        extracted_text=extracted_text,
        toxicity_score=toxicity_score,
        cloudinary_url=upload_result.url,
    )
    insert_result = await database["evidence"].insert_one(evidence_record)

    return ImageAnalysisResponse(
        evidence_id=str(insert_result.inserted_id),
        extracted_text=extracted_text,
        toxicity_score=toxicity_score,
        risk_label=risk_label,
        cloudinary_url=upload_result.url,
        cloudinary_public_id=upload_result.public_id,
    )
