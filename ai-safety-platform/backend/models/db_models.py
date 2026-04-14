from __future__ import annotations

from datetime import datetime, timezone

from bson.binary import Binary

from backend.models.schemas import AnalysisResultPayload, FIRGenerationRequest


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_analysis_record(
    source_type: str,
    analyzed_text: str,
    result: AnalysisResultPayload,
    cloudinary_url: str | None = None,
    cloudinary_public_id: str | None = None,
) -> dict:
    return {
        "source_type": source_type,
        "analyzed_text": analyzed_text,
        "result": result.model_dump(),
        "cloudinary_url": cloudinary_url,
        "cloudinary_public_id": cloudinary_public_id,
        "created_at": utc_now(),
    }


def build_fir_record(
    payload: FIRGenerationRequest,
    analysis_result: AnalysisResultPayload,
    evidence_urls: list[str],
    filename: str,
    pdf_bytes: bytes,
) -> dict:
    return {
        "complainant_name": payload.complainant_name,
        "complainant_contact": payload.complainant_contact,
        "incident_description": payload.incident_description,
        "location": payload.location,
        "incident_datetime": payload.incident_datetime,
        "accused_details": payload.accused_details,
        "additional_notes": payload.additional_notes,
        "subject_is_minor": payload.subject_is_minor,
        "evidence_urls": evidence_urls,
        "analysis_result": analysis_result.model_dump(),
        "filename": filename,
        "pdf_bytes": Binary(pdf_bytes),
        "generated_at": utc_now(),
    }

