from __future__ import annotations

import asyncio
from datetime import datetime

from bson import ObjectId

from backend.config.database import db_manager
from backend.models.db_models import build_fir_record
from backend.models.schemas import FIRGenerationRequest
from backend.services.fir_service import fir_service
from backend.services.toxicity_service import get_safety_analysis_service
from backend.workers.celery_app import celery_app


async def _run_fir_generation(payload_dict: dict, evidence_urls: list[str], job_id: str) -> dict:
    await db_manager.connect()
    database = db_manager.get_database()
    payload = FIRGenerationRequest(**payload_dict)

    analysis_service = get_safety_analysis_service()
    analysis = analysis_service.analyze(
        text=payload.incident_description,
        previous_messages=[item.model_dump() for item in payload.previous_messages],
        language_hint=payload.language_hint,
        subject_is_minor=payload.subject_is_minor,
    )

    filename = fir_service.build_filename(payload.complainant_name)
    pdf_bytes = fir_service.generate_pdf(payload=payload, analysis=analysis, evidence_urls=evidence_urls)
    record = build_fir_record(
        payload=payload,
        analysis_result=analysis,
        evidence_urls=evidence_urls,
        filename=filename,
        pdf_bytes=pdf_bytes,
    )
    insert_result = await database["fir_reports"].insert_one(record)

    await database["fir_jobs"].update_one(
        {"job_id": job_id},
        {
            "$set": {
                "status": "completed",
                "fir_id": str(insert_result.inserted_id),
                "filename": filename,
                "updated_at": datetime.utcnow(),
            }
        },
    )
    return {"fir_id": str(insert_result.inserted_id), "filename": filename}


@celery_app.task(name="generate_fir_pdf")
def generate_fir_pdf(payload_dict: dict, evidence_urls: list[str], job_id: str) -> dict:
    try:
        return asyncio.run(_run_fir_generation(payload_dict, evidence_urls, job_id))
    except Exception as exc:
        async def _mark_failed() -> None:
            await db_manager.connect()
            await db_manager.get_database()["fir_jobs"].update_one(
                {"job_id": job_id},
                {"$set": {"status": "failed", "error": str(exc), "updated_at": datetime.utcnow()}},
            )
        asyncio.run(_mark_failed())
        raise

