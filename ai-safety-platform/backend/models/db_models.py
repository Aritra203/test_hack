from __future__ import annotations

from datetime import datetime, timezone

from bson.binary import Binary


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def build_text_analysis_record(
    text: str,
    toxicity_score: float,
    risk_label: str,
) -> dict:
    return {
        "source_type": "text",
        "text": text,
        "toxicity_score": toxicity_score,
        "risk_label": risk_label,
        "created_at": utc_now(),
    }


def build_evidence_record(
    extracted_text: str,
    toxicity_score: float,
    cloudinary_url: str,
) -> dict:
    return {
        "extracted_text": extracted_text,
        "toxicity_score": toxicity_score,
        "cloudinary_url": cloudinary_url,
        "created_at": utc_now(),
    }


def build_fir_record(
    username: str,
    incident_description: str,
    evidence_notes: str | None,
    evidence_url: str | None,
    evidence_public_id: str | None,
    filename: str,
    pdf_bytes: bytes,
) -> dict:
    return {
        "username": username,
        "incident_description": incident_description,
        "evidence_notes": evidence_notes,
        "evidence_url": evidence_url,
        "evidence_public_id": evidence_public_id,
        "filename": filename,
        "pdf_bytes": Binary(pdf_bytes),
        "generated_at": utc_now(),
    }
