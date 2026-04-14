from __future__ import annotations

import io

from bson import ObjectId
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from backend.config.database import db_manager
from backend.config.settings import settings
from backend.models.db_models import build_fir_record
from backend.models.schemas import FIRGenerationResponse
from backend.services.cloudinary_service import cloudinary_upload_service
from backend.services.fir_service import fir_service


router = APIRouter(tags=["fir"])


@router.post("/generate-fir", response_model=FIRGenerationResponse)
async def generate_fir(
    username: str = Form(..., min_length=2, max_length=120),
    incident_description: str = Form(..., min_length=10, max_length=5000),
    evidence_notes: str | None = Form(default=None, max_length=2000),
    evidence_url: str | None = Form(default=None),
    evidence_public_id: str | None = Form(default=None),
    evidence_file: UploadFile | None = File(default=None),
) -> FIRGenerationResponse:
    if evidence_file is not None:
        upload_result = await cloudinary_upload_service.upload_fastapi_file(
            evidence_file,
            folder_override=f"{settings.cloudinary_folder}/fir-evidence",
        )
        evidence_url = upload_result.url
        evidence_public_id = upload_result.public_id

    if not evidence_url and not evidence_notes:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one evidence input: evidence file, evidence URL, or evidence notes.",
        )

    filename = fir_service.build_filename(username)
    pdf_bytes = await run_in_threadpool(
        fir_service.generate_pdf,
        username,
        incident_description,
        evidence_notes,
        evidence_url,
    )

    database = db_manager.get_database()
    fir_record = build_fir_record(
        username=username,
        incident_description=incident_description,
        evidence_notes=evidence_notes,
        evidence_url=evidence_url,
        evidence_public_id=evidence_public_id,
        filename=filename,
        pdf_bytes=pdf_bytes,
    )
    insert_result = await database["fir_reports"].insert_one(fir_record)
    fir_id = str(insert_result.inserted_id)

    return FIRGenerationResponse(
        fir_id=fir_id,
        filename=filename,
        download_url=f"/download-fir?fir_id={fir_id}",
    )


@router.get("/download-fir")
async def download_fir(fir_id: str):
    if not ObjectId.is_valid(fir_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid fir_id format.",
        )

    database = db_manager.get_database()
    fir_record = await database["fir_reports"].find_one({"_id": ObjectId(fir_id)})
    if not fir_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="FIR report not found.",
        )

    pdf_binary = fir_record.get("pdf_bytes")
    if pdf_binary is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stored FIR payload is missing.",
        )

    filename = fir_record.get("filename", "fir_report.pdf")
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}

    return StreamingResponse(
        io.BytesIO(bytes(pdf_binary)),
        media_type="application/pdf",
        headers=headers,
    )
