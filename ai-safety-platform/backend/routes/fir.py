from __future__ import annotations

import io
import uuid
from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse

from backend.config.database import db_manager
from backend.models.db_models import build_fir_record
from backend.models.schemas import FIRGenerationRequest, FIRGenerationResponse, FIRJobStatusResponse
from backend.services.fir_service import fir_service
from backend.services.toxicity_service import get_safety_analysis_service

try:
    from backend.workers.celery_app import celery_app
except ModuleNotFoundError:
    celery_app = None


router = APIRouter(tags=["fir"])


@router.post("/generate-fir", response_model=FIRGenerationResponse)
async def generate_fir(payload: FIRGenerationRequest) -> FIRGenerationResponse:
    job_id = str(uuid.uuid4())
    evidence_urls = [str(url) for url in payload.evidence_urls]

    await db_manager.get_database()["fir_jobs"].insert_one(
        {
            "job_id": job_id,
            "status": "queued",
            "payload": payload.model_dump(mode="json"),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
    )

    if celery_app is not None:
        celery_app.send_task(
            "generate_fir_pdf",
            args=[payload.model_dump(mode="json"), evidence_urls, job_id],
        )
    else:
        analysis = get_safety_analysis_service().analyze(
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
        insert_result = await db_manager.get_database()["fir_reports"].insert_one(record)
        await db_manager.get_database()["fir_jobs"].update_one(
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
        return FIRGenerationResponse(
            fir_id=str(insert_result.inserted_id),
            filename=filename,
            job_id=job_id,
            status="completed",
        )

    return FIRGenerationResponse(
        fir_id="",
        filename="",
        job_id=job_id,
        status="queued",
    )


@router.get("/fir-job/{job_id}", response_model=FIRJobStatusResponse)
async def fir_job_status(job_id: str) -> FIRJobStatusResponse:
    job = await db_manager.get_database()["fir_jobs"].find_one({"job_id": job_id})
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FIR job not found.")
    return FIRJobStatusResponse(
        job_id=job["job_id"],
        status=job["status"],
        fir_id=job.get("fir_id"),
        filename=job.get("filename"),
        error=job.get("error"),
    )


@router.get("/download-fir")
async def download_fir(fir_id: str):
    if not ObjectId.is_valid(fir_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid fir_id.")

    record = await db_manager.get_database()["fir_reports"].find_one({"_id": ObjectId(fir_id)})
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="FIR not found.")
    pdf_binary = record.get("pdf_bytes")
    if pdf_binary is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="FIR PDF bytes missing.")

    filename = record.get("filename", "fir_report.pdf")
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(io.BytesIO(bytes(pdf_binary)), media_type="application/pdf", headers=headers)

